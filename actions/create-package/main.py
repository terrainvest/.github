#!/usr/bin/env python3

import boto3
from zipfile import ZipFile
import os
import argparse
from os.path import basename
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser()
parser.add_argument('profile', help="- My local credential profile.", nargs='?', const='default')
parser.add_argument('docker', help="- using docker image to deploy lambda.", nargs='?', const='default')
parser.add_argument('-i', '--image', help="- image uri.")

args = parser.parse_args()

def main():
    sessionAws = boto3.Session(profile_name=args.profile, region_name='us-east-1')

    try:
        client = sessionAws.client('lambda')
        return client
    except Exception as e:
        print(f"Error: {e}")

    pass

def updImage(client, functionName):
    print(f"Update function {functionName}")
    client.update_function_code(FunctionName=functionName, ImageUri=args.image)

    pass

def updS3(client, functionName, keyS3):
    print(f"Update function {functionName}")
    client.update_function_code(FunctionName=functionName, S3Bucket=f"default.lambda.package.{args.profile}", S3Key=keyS3)

    pass

def createPackage():
    zipName = f"{os.environ['GITHUB_SHA'][:8]}.zip"

    print("Creating zip file from ./dist folder")    
    with ZipFile(zipName, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk('./dist'):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath, basename(filePath))

    print(f"Zip Name: {zipName}")

    sessionAws = boto3.Session(profile_name=args.profile, region_name='us-east-1')
    clientS3 = sessionAws.client('s3')

    try:
        print(f"Starting upload file to s3...")
        response = clientS3.upload_file(zipName, f"default.lambda.package.{args.profile}", zipName)
        print(f"Finished upload.")
        print(f"Bucket: default.lambda.package.{args.profile}")
        print(f"Object: {zipName}")
    except ClientError as e:
        print(f"Error: {e}")

    return zipName

    pass

if __name__ == '__main__':

    functionName = f"{os.environ['GITHUB_REPOSITORY'].split('/')[1]}-{args.profile}" if args.profile != 'prd' else os.environ['GITHUB_REPOSITORY'].split('/')[1]
    print(f"Function to update: {functionName}")
    client = main()   

    if args.docker == 'true':
        print(f"We are update function using a docker image...")
        updImage(client, functionName)
    else:
        print(f"We will create a zip and upload to S3...")
        zipName = createPackage()        
        updS3(client, functionName, zipName)
