const core = require('@actions/core');
const aws = require('aws-sdk');
const util = require('util');
const dotenv = require('dotenv')

const exec = require('child_process').exec;

const awsProfile = core.getInput('aws_profile');
const registryName = core.getInput('registry');
const imageTag = core.getInput('tag');

console.log(process.env)

async function run(){

    dotenv.config()

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

}

module.exports = run;

if (require.main === module) {
    run();
}