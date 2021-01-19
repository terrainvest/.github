const core = require('@actions/core');
const aws = require('aws-sdk');
const util = require('util');
const dotenv = require('dotenv');
const github = require('@actions/github');
const fs = require("fs");

const exec = require('child_process').exec;

const awsProfile = core.getInput('aws_profile');
const registryName = core.getInput('registry');

console.log(`ACTION PATH + ENV: ${process.env.GITHUB_WORKSPACE}/.env`)
console.log(`CURRENT DIR: ${process.cwd()}`)

if (fs.existsSync(`${process.env.RUNNER_WORKSPACE}/.env`)) {
    console.log("EXISTE .ENV")
}
else {
    core.setFailed(`NAO EXISTE ENV`);
}

async function run(){

    dotenv.config({path:`${github.workspace}/.env`})

    exec(`docker build -t ${registryName} .`, (error, stdout, stderr) => {
        if (stderr){
            core.setFailed(`docker build has failed: ${stderr}`);
        }

        if (error){
            core.setFailed(`docker build has failed: ${error}`);
        }
    });

    let credentials = new aws.SharedIniFileCredentials({profile: awsProfile});
    aws.config.credentials = credentials;
    aws.config.update({region: 'us-east-1'})

    var params = {
        registryIds: [
            process.env[awsProfile.toUpperCase()]
        ]
      };

    let ecr = new aws.ECR();
    let authToken;
    let endPoint;

    ecr.getAuthorizationToken(params, function(err, data) {

        if (err) {
            core.setFailed(`get auth token failed: ${err}`);
        } else {
            authToken = data.authorizationData[0].authorizationToken
            endPoint = data.authorizationData[0].proxyEndpoint.replace("https://", "")
        }

      });

    exec(`docker login -u AWS -p ${authToken} ${endPoint}`, (error, stdout, stderr) => {
        if (stderr){
            core.setFailed(`docker login has failed: ${stderr}`);
        }

        if (error){
            core.setFailed(`docker login has failed: ${error}`);
        }
    });

    let imageTag = process.env.GITHUB_SHA.substring(0, 8)

    let imageECR = `${endPoint}/${registryName}:${imageTag}`

    exec(`docker tag ${registryName}:${imageTag} ${imageECR}`, (error, stdout, stderr) => {
        if (stderr){
            core.setFailed(`docker login has failed: ${stderr}`);
        }

        if (error){
            core.setFailed(`docker login has failed: ${error}`);
        }
    });

    exec(`docker push ${imageECR}`, (error, stdout, stderr) => {
        if (stderr){
            core.setFailed(`docker push has failed: ${stderr}`);
        }

        if (error){
            core.setFailed(`docker push has failed: ${error}`);
        }
    });

    core.setOutput("image", imageECR);

    core.setOutput("repository", process.env.GITHUB_REPOSITORY.split("/")[1])

}

module.exports = run;

if (require.main === module) {
    run();
}