import os
import sys

def main(aws_profile):
    rootDir = os.path.expanduser('~')    

    try:
        os.mkdir(f"{rootDir}/.aws")
    except OSError:
        print ("Creation of the directory .aws failed")
    else:
        print ("Successfully created the directory .aws ")

    ORG_TF_AWS_KEY_ID = os.environ["ORG_TF_AWS_KEY_ID"]
    ORG_TF_AWS_SECRET_KEY = os.environ["ORG_TF_AWS_SECRET_KEY"]
    
    HML_TF_AWS_KEY_ID = os.environ["HML_TF_AWS_KEY_ID"]
    HML_TF_AWS_SECRET_KEY = os.environ["HML_TF_AWS_SECRET_KEY"]
    
    PRD_TF_AWS_KEY_ID = os.environ["PRD_TF_AWS_KEY_ID"]
    PRD_TF_AWS_SECRET_KEY = os.environ["PRD_TF_AWS_SECRET_KEY"]    

    fileAws = open(f"{rootDir}/.aws/credentials","a+")

    fileAws.write("[org]")
    fileAws.write(f"aws_access_key_id = { ORG_TF_AWS_KEY_ID }")
    fileAws.write(f"aws_secret_access_key = { ORG_TF_AWS_SECRET_KEY }")

    fileAws.write("[hml]")
    fileAws.write(f"aws_access_key_id = { HML_TF_AWS_KEY_ID }")
    fileAws.write(f"aws_secret_access_key = { HML_TF_AWS_SECRET_KEY }")

    fileAws.write("[prd]")
    fileAws.write(f"aws_access_key_id = { PRD_TF_AWS_KEY_ID }")
    fileAws.write(f"aws_secret_access_key = { PRD_TF_AWS_SECRET_KEY }")

    fileAws.close()

    os.environ["AWS_PROFILE"] = aws_profile

if __name__ == "__main__":
    main(sys.argv[1])