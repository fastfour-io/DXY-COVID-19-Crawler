import json
import os
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from service.crawler import Crawler

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[AwsLambdaIntegration()]
)

def lambda_handler(event, context):
    crawler = Crawler()
    crawler.run()
    return {
        'statusCode': 200,
        'body': json.dumps('Crawled successfully')
    }
