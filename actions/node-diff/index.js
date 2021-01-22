const core = require('@actions/core');
const util = require('util');
const exec = util.promisify(require('child_process').exec);

var currentCommit = core.getInput('current_commit');

if (core.getInput('git_event') === 'pull_request'){
  currentCommit = core.getInput('pull_request_commit');
}

const rootDir = core.getInput('rootDir');  

console.log(`Inputs: currentCommit - ${currentCommit}\trootDir - ${rootDir}`)

async function getPath() {
  try {

      let { stdout } = await exec('git diff-tree --no-commit-id --name-only -r -c ' + currentCommit);      
      
      if(!Boolean(stdout)){

        let commitPullReq = core.getInput('pull_request_commit')

        let { stdout2 } = await exec('git diff-tree --no-commit-id --name-only -r -c ' + commitPullReq);

        if(Boolean(stdout2)){
          stdout = stdout2
        } else{

          core.setFailed(`Nothing return from git diff-tree command at commit: ${currentCommit} or ${commitPullReq}`);

        }
        
      }

      console.log("Files that have changed:\n" + stdout);

      arrayPath = stdout.split("\n")
      arrayPath.pop()      

      return arrayPath

  }catch (err){
     console.error(err);
     core.setFailed(err);
  };
};

getPath()
  .then(
    arrayPath => setOutput(arrayPath)
  )

  async function setOutput(arrayPath) {

    let objPath = {};
    objPath['path'] = [];

    const promises = arrayPath.map(async (item) => {
    
      if(item.match(/\b.tf\b/)){
        
        itemArray = item.split('/');     
  
        if(itemArray[0] === rootDir){
        
          let pathString = rootDir + "/";
  
          for (let i = 1; i < itemArray.length - 1; i++) {          
            pathString += itemArray[i] + "/";
  
            if(pathString.split('/').length == itemArray.length){
              if(!objPath['path'].includes(pathString)){
                objPath['path'].push(pathString)
              }            
            }          
  
          }               
  
        } else{
          core.setFailed("rootDir not found in current repo!");
          throw new Error("rootDir not found in current repo!");
        } 

      }         

    });
    
    await Promise.all(promises)          
          .catch(err => core.setFailed("error: " + err))

    core.setOutput("path", JSON.stringify(objPath));
    console.log(`output path: ${JSON.stringify(objPath)}`)

  }