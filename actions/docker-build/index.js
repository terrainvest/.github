'use strict';

const core = require('@actions/core');
const aws = require('aws-sdk');
const dotenv = require('dotenv');
//const util = require('util');
const exec = require('child_process').exec;

dotenv.config({path: `${process.env.GITHUB_WORKSPACE}/.github/.env.lambda` });
const registryName = process.env["REGISTRY"];
const awsProfile = core.getInput('aws_profile');
const imageTag = process.env.GITHUB_SHA.substring(0, 8)

async function dockerBuild(){

    console.log(`Running docker build, image: ${registryName}`);
    return new Promise( (resolve, reject) => {
        exec(`docker build . --file Dockerfile --tag ${registryName}`, (error, stdout, stderr) => {
        if (error){             
            console.error(`Error build: ${error}`)
        }        
        console.log(`Response build: ${stdout}`);
        resolve(stdout);
    });
        
    });

}

async function dockerLogin(){

    let credentials = new aws.SharedIniFileCredentials({profile: awsProfile});
    aws.config.credentials = credentials;
    aws.config.update({region: 'us-east-1'})

    var params = {
        registryIds: [
            process.env[awsProfile.toUpperCase()]
        ]
      };

    let ecr = new aws.ECR();

    ecr.getAuthorizationToken(params, function(err, data) {
        if (err) { 
            core.setFailed(`get auth token failed: ${err}`); 
            throw err;
        }

        let authToken = Buffer.from(data.authorizationData[0].authorizationToken, 'base64').toString('ascii').replace("AWS:", "");
        let endPoint = data.authorizationData[0].proxyEndpoint.replace("https://", "");

        console.log(`Getting login of ecr: ${endPoint}`);
        exec(`docker login -u AWS -p ${authToken} ${endPoint}`, (error, stdout, stderr) => {
            if (stderr || error){ 
                let responseError = stderr ? stderr : error;
                if(!responseError.toLowerCase().includes("warning")){
                    core.setFailed(`Error at docker login: ${responseError}`);
                    return;
                }
            }            
            console.log(`Response Login: ${stdout}`)

            dockerTagAndPush(endPoint);

        });

    });

}

async function dockerTagAndPush(endPoint){   

    let imageECR = `${endPoint}/${registryName}:${imageTag}`

    console.log(`docker tag ${registryName} ${imageECR}`);
    exec(`docker tag ${registryName} ${imageECR}`, (error, stdout, stderr) => {
            
        if (error){             
                console.error(`Error at docker tag: ${responseError}`);
        }   

        console.log(`docker push ${imageECR}`);
        exec(`docker push ${imageECR}`, (error, stdout, stderr) => {
            if (stderr || error){ 
                let responseError = stderr ? stderr : error;
                if(!responseError.toLowerCase().includes("warning")){
                    core.setFailed(`Error at docker push: ${responseError}`);
                    return;
                }
            } 
            
            console.log(`Response push: ${stdout}`)

        });

    });    

    core.setOutput("image", imageECR);
    core.setOutput("repository", process.env.GITHUB_REPOSITORY.split("/")[1])

}

try{
    let result = dockerBuild();
    result.then(response => {
        console.log(`Result Promise: ${response}`)
        exec(`docker images`, (error, stdout, stderr) => {
            if (error){             
                console.error(`DOCKER IMAGES ERROR: ${error}`)
            }        
            console.log(`Docker Images: ${stdout}`);
            resolve(stdout);
        });
    })
    console.log(`Result: ${result}`);

} catch(e){
    console.error(e) 
}
    

    //dockerBuild()
    //    .then(response => {
    //        console.log(response);
    //        dockerLogin();
    //    })
    //    .catch(e => {
    //        if(!e.toLowerCase().includes("warning")){
    //            core.setFailed(`Error docker build: ${e}`)
    //        }
//
    //    });
