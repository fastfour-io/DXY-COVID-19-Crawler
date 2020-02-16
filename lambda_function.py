import json
from service.crawler import Crawler

def lambda_handler(event, context):
    crawler = Crawler()
    crawler.run()
    return {
        'statusCode': 200,
        'body': json.dumps('Crawled successfully')
    }
