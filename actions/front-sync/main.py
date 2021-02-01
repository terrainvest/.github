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
        response = client.list_objects(Bucket=args.bucket)

        deleteKeys = {'Objects': []}
        for content in response['Contents']:
            keyMap = dict()
            keyMap['Key'] = content['Key']
            deleteKeys['Objects'].append(keyMap)

        client.delete_objects(Bucket=args.bucket, Delete=str(deleteKeys))

    except Exception as e:
        sys.exit(f'Error on delete s3: {e}')

    pass


def syncBuild(client):
    try:
        for folderName, subfolder, filenames in os.walk(f"{args.folder}"):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                filePathReplaced = filePath.replace(f"{args.folder}/", "")
                client.upload_file(filePath, args.bucket, filePathReplaced)

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