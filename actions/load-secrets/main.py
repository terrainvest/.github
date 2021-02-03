#!/usr/bin/env python3

import json
import os
import subprocess


def main():
    jsonRaw = os.getenv("SECRETS_CONTEXT")
    jsonData = json.load(jsonRaw)

    for key, value in jsonData.items():
        os.system(f'echo "{key}={value}" >> $GITHUB_ENV')

if __name__ == '__main__':        
    main()