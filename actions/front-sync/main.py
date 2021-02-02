#!/usr/bin/env python3

import boto3
import sys
import argparse
import os
from time import time


parser = argparse.ArgumentParser()
parser.add_argument('profile', help="- My local credential profile.", nargs='?', const='default')
parser.add_argument('folder', help="- folder that node has builded.", nargs='?', const='default')
parser.add_argument('cfid', help="- cf id to invalidade.", nargs='?', const='default')
parser.add_argument('bucket', help="- bucket to sync.", nargs='?', const='default')

args = parser.parse_args()


def main():
    print(f"Running at profile: {args.profile}")
    sessionAws = boto3.Session(profile_name=args.profile, region_name='us-east-1')

    try:
        clientS3 = sessionAws.client('s3')
        deleteKeys(clientS3)
        syncBuild(clientS3)

        clientCF = sessionAws.client('cloudfront')
        invalidateCF(clientCF)

    except Exception as e:
        sys.exit(f'Error on main: {e}')

    pass


def deleteKeys(client):
    try:
        print(f"Get Keys to delete")
        response = client.list_objects(Bucket=str(args.bucket))

        print("Filter keys")
        if 'Contents' in response:
            deleteKeys = {'Objects': []}
            for content in response['Contents']:
                keyMap = dict()
                keyMap['Key'] = content['Key']
                deleteKeys['Objects'].append(keyMap)

            print(f"Keys to delete: {str(deleteKeys)}")
            client.delete_objects(Bucket=args.bucket, Delete=deleteKeys)
        else:
            print("Bucket already empty")

    except Exception as e:
        sys.exit(f'Error on delete s3: {e}')

    pass


def syncBuild(client):
    try:
        print(f"Syncing new files from folder: {os.environ['GITHUB_WORKSPACE']}/{args.folder}")
        print(os.path.isdir(f"{os.environ['GITHUB_WORKSPACE']}/{args.folder}"))
        for folderName, subfolder, filenames in os.walk(f"{os.environ['GITHUB_WORKSPACE']}/{args.folder}/"):
            for filename in filenames:                
                filePath = os.path.join(folderName, filename)
                filePathReplaced = filePath.replace(f"{args.folder}/", "")
                print(f"Uploading file: {filePathReplaced}")
                response = client.upload_file(filePath, args.bucket, filePathReplaced)
                print(f"Response: {response}")

    except Exception as e:
        sys.exit(f'Error sync: {e}')

    pass


def invalidateCF(client):
    try:
        client.create_invalidation(
            DistributionId=args.cfid,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': [
                        '/*'
                    ]
                },
                'CallerReference': str(time()).replace(".", "")
            }
        )

    except Exception as e:
        sys.exit(f'Error invalidation: {e}')


if __name__ == '__main__':
    main()