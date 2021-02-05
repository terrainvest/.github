#!/usr/bin/env python3

import mimetypes
import boto3
import sys
import argparse
import os
from time import time


parser = argparse.ArgumentParser()
parser.add_argument('prSha', help="- prSha to key.", nargs='?', const='default')
parser.add_argument('action', help="- action to key.", nargs='?', const='put')

args = parser.parse_args()


def main():
    print(f"Running at profile: org")
    sessionAws = boto3.Session(profile_name='org', region_name='us-east-1')

    try:
        clientS3 = sessionAws.resource('s3')

        if args.action == 'put':
            syncFile(clientS3)
        else:
            getFile(clientS3)

    except Exception as e:
        sys.exit(f'Error on main: {e}')

    pass

def syncFile(client):
    try:
        print(f"Syncing file: plan-file.tfplan")
        print(f"Key of file: {args.prSha}/plan-file.tfplan")

        client.meta.client.upload_file('plan-file.tfplan', 'default.lambda.package.org', f"{args.prSha}/plan-file.tfplan")

    except Exception as e:
        sys.exit(f'Error sync: {e}')

    pass

def getFile(client):
    try:
        print(f"Downloading file: plan-file.tfplan")
        print(f"Key of file: {args.prSha}/plan-file.tfplan")

        client.meta.client.download_file('default.lambda.package.org', f"{args.prSha}/plan-file.tfplan", "plan-file.tfplan")

    except Exception as e:
        sys.exit(f'Error getting file: {e}')

    pass

if __name__ == '__main__':
    main()