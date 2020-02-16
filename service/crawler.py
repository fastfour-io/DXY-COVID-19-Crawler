"""
@ProjectName: DXY-2019-nCov-Crawler
@FileName: crawler.py
@Author: Jiabao Lin
@Date: 2020/1/21
"""
from bs4 import BeautifulSoup
from service.nameMap import country_type_map, city_name_map, country_name_map, continent_name_map
import os
import datetime
import re
import json
import time
import logging
import datetime
import requests
from github import Github
from github import InputGitTreeElement

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}


class Crawler:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update(headers)
        self.crawl_timestamp = int()

    def run(self):
            self.crawler()

    def crawler(self):
        while True:
            self.crawl_timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)
            try:
                r = self.session.get(url='https://3g.dxy.cn/newh5/view/pneumonia')
            except requests.exceptions.ChunkedEncodingError:
                continue
            soup = BeautifulSoup(r.content, 'lxml')

            overall_information = re.search(r'\{("id".*?)\]\}', str(soup.find('script', attrs={'id': 'getStatisticsService'})))
            province_information = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getListByCountryTypeService1'})))
            area_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getAreaStat'})))
            abroad_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getListByCountryTypeService2'})))

            if not overall_information or not province_information or not area_information:
                continue

            overall_information = self.overall_parser(overall_information=overall_information)
            province_information = self.province_parser(province_information=province_information)
            area_information = self.area_parser(area_information=area_information)
            abroad_information = self.abroad_parser(abroad_information=abroad_information)

            print(json.dumps(area_information, indent=4, sort_keys=True))
            with open('area.json', 'w') as outfile:
                json.dump(area_information, outfile)
            with open('overall.json', 'w') as outfile:
                json.dump(overall_information, outfile)
            with open('province.json', 'w') as outfile:
                json.dump(province_information, outfile)
            with open('abroad.json', 'w') as outfile:
                json.dump(abroad_information, outfile)
            file_list=[
                os.path.abspath("area.json"),
                os.path.abspath("overall.json"),
                os.path.abspath("province.json"),
                os.path.abspath("abroad.json")
            ]
            file_names=[
                "area.json",
                "overall.json",
                "province.json",
                "abroad.json"
            ]

            commit_message="update data {}".format(datetime.datetime.now())
            self.commit_file(file_list, file_names, commit_message)

            break

        logger.info('Successfully crawled.')

    def overall_parser(self, overall_information):
        overall_information = json.loads(overall_information.group(0))
        overall_information.pop('id')
        overall_information.pop('createTime')
        overall_information.pop('modifyTime')
        overall_information.pop('imgUrl')
        overall_information.pop('deleted')
        overall_information['countRemark'] = overall_information['countRemark'].replace(' 疑似', '，疑似').replace(' 治愈', '，治愈').replace(' 死亡', '，死亡').replace(' ', '')
        return overall_information

    def province_parser(self, province_information):
        provinces = json.loads(province_information.group(0))
        for province in provinces:
            province.pop('id')
            province.pop('tags')
            province.pop('sort')
            province['comment'] = province['comment'].replace(' ', '')

            province['provinceEnglishName'] = city_name_map[province['provinceShortName']]['engName']
            province['crawlTime'] = self.crawl_timestamp
            province['country'] = country_type_map.get(province['countryType'])
        return provinces

    def area_parser(self, area_information):
        area_information = json.loads(area_information.group(0))
        for area in area_information:
            area['comment'] = area['comment'].replace(' ', '')

            # Because the cities are given other attributes,
            # this part should not be used when checking the identical document.
            cities_backup = area.pop('cities')

            # if self.db.find_one(collection='DXYArea', data=area):
            #     continue

            # If this document is not in current database, insert this attribute back to the document.
            area['cities'] = cities_backup

            area['countryName'] = '中国'
            area['countryEnglishName'] = 'China'
            area['continentName'] = '亚洲'
            area['continentEnglishName'] = 'Asia'
            area['provinceEnglishName'] = city_name_map[area['provinceShortName']]['engName']

            for city in area['cities']:
                if city['cityName'] != '待明确地区':
                    try:
                        city['cityEnglishName'] = city_name_map[area['provinceShortName']]['cities'][city['cityName']]
                    except KeyError:
                        print(area['provinceShortName'], city['cityName'])
                        pass
                else:
                    city['cityEnglishName'] = 'Area not defined'

        return area_information

    def abroad_parser(self, abroad_information):
        countries = json.loads(abroad_information.group(0))
        for country in countries:
            country.pop('id')
            country.pop('tags')
            country.pop('countryType')
            country.pop('provinceId')
            country.pop('cityName')
            country.pop('sort')
            # The original provinceShortName are blank string
            country.pop('provinceShortName')
            # Rename the key continents to continentName
            country['continentName'] = country.pop('continents')

            country['comment'] = country['comment'].replace(' ', '')

            # if self.db.find_one(collection='DXYArea', data=country):
            #     continue

            country['countryName'] = country.get('provinceName')
            country['provinceShortName'] = country.get('provinceName')
            country['continentEnglishName'] = continent_name_map.get(country['continentName'])
            country['countryEnglishName'] = country_name_map.get(country['countryName'])
            country['provinceEnglishName'] = country_name_map.get(country['countryName'])
        return countries

    def commit_file(self, file_list, file_names, commit_message):
        user=os.environ["GITHUB_USER"]
        password=os.environ["GITHUB_TOKEN"]

        g = Github(user, password)
        repo = g.get_user().get_repo("covid-19.global-event-tracker.website-data")
        master_ref = repo.get_git_ref('heads/master')
        master_sha = master_ref.object.sha
        base_tree = repo.get_git_tree(master_sha)
        element_list = list()
        for i, entry in enumerate(file_list):
            with open(entry) as input_file:
                data = input_file.read()
            element = InputGitTreeElement(file_names[i], '100644', 'blob', data)
            element_list.append(element)
        tree = repo.create_git_tree(element_list, base_tree)
        parent = repo.get_git_commit(master_sha)
        commit = repo.create_git_commit(commit_message, tree, [parent])
        master_ref.edit(commit.sha)



if __name__ == '__main__':
    crawler = Crawler()
    crawler.run()
