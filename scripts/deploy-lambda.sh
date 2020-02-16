#!/bin/bash

# Requires:
#  pip3 install awscli

set -e
set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Move to repository root directory
rootDir="${DIR}/.."

cd $rootDir

# Install packages
pip3 install \
  --target ./package \
  -r requirements.txt
cd package

zip -r9 "$rootDir/function.zip" .

# Add function code
cd $rootDir
zip -g "$rootDir/function.zip" lambda_function.py service/crawler.py service/nameMap.py

# Update function in AWS
aws lambda update-function-code \
  --function-name covid19Crawler \
  --zip-file fileb://function.zip
