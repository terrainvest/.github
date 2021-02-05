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
parser.add_argument('key', help="- key to s3.", nargs='?', const='hml')

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
        print(f"Key of file: {args.prSha}/{args.key}plan-file.tfplan")

        client.meta.client.upload_file('plan-file.tfplan', 'default.lambda.package.org', f"{args.prSha}/{args.key}plan-file.tfplan")

    except Exception as e:
        sys.exit(f'Error sync: {e}')

    pass


def getFile(client):
    try:
        print(f"Searching of file in key: {args.prSha}")

        response = client.meta.client.list_objects(Bucket='default.lambda.package.org', Prefix=args.prSha)

        if 'Contents' in response:
            print(f"Downloading file: {response['Contents'][0]['Key']}")
            stIndex = response['Contents'][0]['Key'].index(f"/") + 1
            lastIndex = response['Contents'][0]['Key'].rindex(f"/") + 1
            env = response['Contents'][0]['Key'][stIndex:lastIndex]
            profile = env.split('/')[1]

            client.meta.client.download_file('default.lambda.package.org', response['Contents'][0]['Key'],
                                             f"{env}plan-file.tfplan")
            os.system(f'echo "::set-output name=env_apply::{env}"')
            os.system(f'echo "::set-output name=aws_profile::{profile}"')

    except Exception as e:
        sys.exit(f'Error getting file: {e}')

    pass

if __name__ == '__main__':
    main()