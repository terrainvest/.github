import os
import sys

def main(aws_profile, root_path):
    rootDir = os.path.expanduser('~')
    print(root_path)

    try:
        os.mkdir(f"{root_path}/.aws")
    except OSError:
        print (f"Creation of the directory {root_path}/.aws failed")
    else:
        print (f"Successfully created the directory {root_path}/.aws")

    ORG_TF_AWS_KEY_ID = os.environ["ORG_TF_AWS_KEY_ID"]
    ORG_TF_AWS_SECRET_KEY = os.environ["ORG_TF_AWS_SECRET_KEY"]
    
    HML_TF_AWS_KEY_ID = os.environ["HML_TF_AWS_KEY_ID"]
    HML_TF_AWS_SECRET_KEY = os.environ["HML_TF_AWS_SECRET_KEY"]
    
    PRD_TF_AWS_KEY_ID = os.environ["PRD_TF_AWS_KEY_ID"]
    PRD_TF_AWS_SECRET_KEY = os.environ["PRD_TF_AWS_SECRET_KEY"]    

    fileAws = open(f"{root_path}/.aws/credentials","a+")

    fileAws.write("[org]")
    fileAws.write(f"aws_access_key_id = { ORG_TF_AWS_KEY_ID }")
    fileAws.write(f"aws_secret_access_key = { ORG_TF_AWS_SECRET_KEY }")

    fileAws.write("[dev]")
    fileAws.write(f"aws_access_key_id = { HML_TF_AWS_KEY_ID }")
    fileAws.write(f"aws_secret_access_key = { HML_TF_AWS_SECRET_KEY }")

    fileAws.write("[hml]")
    fileAws.write(f"aws_access_key_id = { HML_TF_AWS_KEY_ID }")
    fileAws.write(f"aws_secret_access_key = { HML_TF_AWS_SECRET_KEY }")

    fileAws.write("[prd]")
    fileAws.write(f"aws_access_key_id = { PRD_TF_AWS_KEY_ID }")
    fileAws.write(f"aws_secret_access_key = { PRD_TF_AWS_SECRET_KEY }")

    fileAws.close()    

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])