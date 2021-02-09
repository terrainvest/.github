#!/usr/bin/env python3

import mimetypes
import boto3
import sys
import argparse
import os
import hashlib


parser = argparse.ArgumentParser()
parser.add_argument('prUrl', help="- pr_url to key.", nargs='?', const='default')
parser.add_argument('action', help="- action to key.", nargs='?', const='put')
parser.add_argument('key', help="- key to s3.", nargs='?', const='hml')

args = parser.parse_args()


def main():
    print(f"Running at profile: org")
    sessionAws = boto3.Session(profile_name='org', region_name='us-east-1')

    try:
        hashKey()

        clientS3 = sessionAws.resource('s3')

        if args.action == 'put':
            syncFile(clientS3)
        else:
            getFile(clientS3)

    except Exception as e:
        sys.exit(f'Error on main: {e}')

    pass


def hashKey():
    keys = args.prUrl.split('terrainvest/')
    hash_object = hashlib.sha1(keys[1].encode())
    args.prUrl = hash_object.hexdigest()

    pass


def syncFile(client):
    try:
        print(f"Syncing file: plan-file.tfplan")
        print(f"Key of file: {args.prUrl}/{args.key}plan-file.tfplan")

        client.meta.client.upload_file(f'{args.key}plan-file.tfplan', 'default.lambda.package.org', f"{args.prUrl}/{args.key}plan-file.tfplan")

    except Exception as e:
        sys.exit(f'Error sync: {e}')

    pass


def getFile(client):
    try:
        print(f"Searching of file in key: {args.prUrl}")

        response = client.meta.client.list_objects(Bucket='default.lambda.package.org', Prefix=args.prUrl)

        if 'Contents' in response:
            print(f"Downloading file: {response['Contents'][0]['Key']}")
            stIndex = response['Contents'][0]['Key'].index(f"/") + 1
            lastIndex = response['Contents'][0]['Key'].rindex(f"/") + 1
            env = response['Contents'][0]['Key'][stIndex:lastIndex]
            profile = env.split('/')[1]

            print(f'Save file at: {env}plan-file.tfplan')
            if not os.path.isdir(env):
                os.makedirs(env)
            client.meta.client.download_file('default.lambda.package.org', response['Contents'][0]['Key'],
                                             f'{env}plan-file.tfplan')
            os.system(f'echo "AWS_PROFILE={profile}" >> $GITHUB_ENV')
            os.system(f'echo "ENV_APPLY={env}" >> $GITHUB_ENV')

    except Exception as e:
        sys.exit(f'Error getting file: {e}')

    pass


if __name__ == '__main__':
    main()