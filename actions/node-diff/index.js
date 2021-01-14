const core = require('@actions/core');
const util = require('util');

try {  
  const currentCommit = core.getInput('currentCommit');
  const rootDir = core.getInput('rootDir');  
} catch (error) {
  core.setFailed(error.message);
}

async function getPath() {
  try {
      const { stdout } = await exec('git diff-tree --no-commit-id --name-only -r -c ' + currentCommit);
      
      arrayPath = stdout.split("\n")
      arrayPath.pop()

      return arrayPath

  }catch (err){
     console.error(err);
  };
};

const exec = util.promisify(require('child_process').exec);

getPath()
  .then(
    arrayPath => setOutput(arrayPath)
  )

  async function setOutput(arrayPath) {

    let paths = [];

    const promises = arrayPath.map(async (item) => {
    
      itemArray = item.split('/');     

      if(itemArray[0] === rootDir){

        let pathString = rootDir + "/";

        for (let i = 1; i < itemArray.length - 1; i++) {          
          pathString += itemArray[i] + "/";
          
          if(!paths.includes(pathString)){
            paths.push(pathString)
          }

        }               

      } else{
        throw new Error("rootDir not found in current repo!");
      }          

    });
    
    await Promise.all(promises)          
          .catch(err => console.log("error: " + err))

    core.setOutput("paths", paths);

  }