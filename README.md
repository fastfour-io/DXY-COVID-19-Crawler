# COVID-19/2019-nCoV Infection Data Realtime Crawler

[![license](https://img.shields.io/github/license/BlankerL/DXY-COVID-19-Crawler)](https://github.com/BlankerL/DXY-COVID-19-Crawler/blob/master/LICENSE)

COVID-19/2019-nCoV infection data realtime crawler, the data source is [Ding Xiang Yuan](https://3g.dxy.cn/newh5/view/pneumonia).

Please reduce the deployment of crawlers in order to prevent the crawlers 
from flooding the DXY and occupying too much traffic, 
such that other users in need cannot get the data in time. 

**This project is subject to the MIT open source license. 
If you use the API, please declare the reference in your project.**

## Changes from the original
The original crawler, https://github.com/BlankerL/DXY-COVID-19-Crawler has been changed:

 - The version does not store state in a DB, it commits and pushes JSON files to github
 - Some wrappers have been written to get it into a Lambda
 - Sentry.io integration

I wanted a way to access this data without having to build and maintain an API server. This minor refactoring ensures
the latest data is available in the https://github.com/fastfour-io/covid-19.global-event-tracker.website-data
repository.

Currently the lambda function runs once every 2 minutes.
