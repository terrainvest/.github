import subprocess
import json
import os
import shutil


def readPackage():
    jsonFile = open('./package.json')
    jsonData = json.load(jsonFile)

    retorno = False
    if 'build' in jsonData['scripts']:
        retorno = True

    return retorno, jsonData['main']

def createDist(mainFile):
    print("mkdir dist")
    if not os.path.exists("dist"):
        os.makedirs("dist")

    print("copying files...")
    shutil.copyfile(mainFile, './dist')
    shutil.copyfile("package.json", './dist')
    shutil.copyfile("package-lock.json", './dist')

    pass

def main(build, mainFile):
    try:
        if build:
            print("exec npm run build")
            subprocess.run(["npm", "run", "build"])
        else:
            print("create dist folder")
            createDist(mainFile)

    except Exception as e:
        print(f"ERROR: {e}")

    pass

if __name__ == '__main__':
    print("Looking for Build script")
    buildNode, mainFile = readPackage()
    print(f"Find build script: {buildNode}")
    main(buildNode, mainFile)