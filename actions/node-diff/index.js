const core = require('@actions/core');
const util = require('util');

const currentCommit = core.getInput('current_commit');
const rootDir = core.getInput('rootDir');  

console.log("Inputs: currentCommit - ${currentCommit}\trootDir - ${rootDir}")


async function getPath() {
  try {
      const { stdout } = await exec('git diff-tree --no-commit-id --name-only -r -c ' + currentCommit);
      
      if(!Boolean(stdout)){
        core.setFailed("Nothing return from git diff-tree command at commit: "+ currentCommit);
      }

      console.log("Files that have changed:\n" + stdout);

      arrayPath = stdout.split("\n")
      arrayPath.pop()

      console.error(err);

      return arrayPath

  }catch (err){
     console.error(err);
     core.setFailed(err);
  };
};

const exec = util.promisify(require('child_process').exec);

getPath()
  .then(
    arrayPath => setOutput(arrayPath)
  )

  async function setOutput(arrayPath) {

    let objPath = {};
    objPath['path'] = [];

    const promises = arrayPath.map(async (item) => {
    
      itemArray = item.split('/');     

      if(itemArray[0] === rootDir){

        let pathString = rootDir + "/";

        for (let i = 1; i < itemArray.length - 1; i++) {          
          pathString += itemArray[i] + "/";
          
          if(!objPath['path'].includes(pathString)){
            objPath['path'].push(pathString)
          }

        }               

      } else{
        core.setFailed("rootDir not found in current repo!");
        throw new Error("rootDir not found in current repo!");
      }          

    });
    
    await Promise.all(promises)          
          .catch(err => core.setFailed("error: " + err))

    core.setOutput("path", JSON.stringify(objPath));
    console.log("output path: ${JSON.stringify(objPath)}")

  }