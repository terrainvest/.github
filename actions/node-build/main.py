import subprocess
import json
import os
import shutil
import sys


def readPackage():
    jsonFile = open('./package.json')
    jsonData = json.load(jsonFile)

    retorno = False
    test = True
    mainFile = ""

    if 'build' in jsonData['scripts']:
        retorno = True

    if 'main' in jsonData:
        mainFile = jsonData['main']

    if 'test' not in jsonData['scripts']:
        test = False

    return retorno, mainFile, test

def createDist(mainFile):
    print("mkdir dist")
    if not os.path.exists("dist"):
        os.makedirs("dist")

    print("copying files...")
    shutil.copyfile(mainFile, f'./dist/{mainFile}')
    shutil.copyfile("package.json", './dist/package.json')
    shutil.copyfile("package-lock.json", './dist/package-lock.json')

    if sys.argv[1] != "lambda":
        shutil.copytree("./node_modules", './dist/node_modules')

    pass

def useYarn():
    return os.path.exists(".yarnrc")

def main(build, mainFile, runTest):
    try:

        package = "npm"

        if build:
            if useYarn():
                print("Installing yarn")
                os.system(["npm", "install", "-g", "yarn"])
                print("Yarn version")
                os.system(["yarn", "--version"])
                package = "yarn"
            
            nodeEnv = os.getenv["NODE_ENV"]
            print(f"start build using NODE_ENV: {nodeEnv}")

            print(f"running {package} install")
            os.system(f"{package} install"])
            print(f"running {package} build")
            os.system(f"{package} run build"])

            if runTest:
                os.system(f"{package} test"])

        else:
            print("create dist folder")
            createDist(mainFile)        

    except Exception as e:
        print(f"ERROR: {e}")

    pass

if __name__ == '__main__':
    print("Looking for Build script")    
    buildNode, mainFile, runTest = readPackage()
    print(f"Find build script: {buildNode}")
    main(buildNode, mainFile, runTest)