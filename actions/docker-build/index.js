'use strict';

const core = require('@actions/core');
const aws = require('aws-sdk');
const dotenv = require('dotenv');
//const util = require('util');
const exec = require('child_process').exec;

dotenv.config({path: `${process.env.GITHUB_WORKSPACE}/.github/.env.lambda` });
const awsProfile = core.getInput('aws_profile');
const imageTag = process.env.GITHUB_SHA.substring(0, 8)

const registryName = awsProfile === "prd" ? process.env["REGISTRY"] : `${process.env["REGISTRY"]}.${awsProfile}`;

async function dockerBuild(){

    console.log(`Running docker build, image: ${registryName}`);
    return new Promise( (resolve, reject) => {
        exec(`docker build . --file ${process.env.GITHUB_WORKSPACE}/Dockerfile --tag ${registryName}`, (error, stdout, stderr) => {
        if (error){             
            console.error(`Error build: ${error}`)
        }               
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
            if (error){ 
                console.error(`Error login: ${error}`)
            }            
            console.log(`Response Login: ${stdout}`)

            let imageECR = `${endPoint}/${registryName}`

            Promise.all([dockerTag(endPoint, imageTag), dockerTag(endPoint, "latest")]).then(values => dockerPush(imageECR));

        });

    });

}

async function dockerTag(endPoint, imageTag){   

    return new Promise( (resolve) => {

        let imageECR = `${endPoint}/${registryName}:${imageTag}`
        console.log(`docker tag ${registryName} ${imageECR}`);

        exec(`docker tag ${registryName} ${imageECR}`, (error, stdout, stderr) => {

            if (error){             
                console.error(`Error at docker tag: ${responseError}`);
            }

            resolve(stdout)

        })

    })    

}

async function dockerPush(imageEcr){
    
    console.log(`docker push ${imageECR}`);
        exec(`docker push ${imageECR}`, (error, stdout, stderr) => {
            if (error){ 
                console.error(`Error push: ${error}`)
            } 
            
            console.log(`Response push: ${stdout}`)

        });

    core.setOutput("image", imageECR);

    let repository = process.env.GITHUB_REPOSITORY.split("/")[1];
    repository = awsProfile === "prd" ? repository : `${repository}-${awsProfile}`

    core.setOutput("repository", repository)

}

try{
    let result = dockerBuild();
    result.then(response => {
        console.log(`Response Build: ${response}`)
        dockerLogin();
    })    

} catch(e){
    console.error(e) 
}