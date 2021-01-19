const core = require('@actions/core');
const aws = require('aws-sdk');
const dotenv = require('dotenv');

const exec = require('child_process').exec;

const awsProfile = core.getInput('aws_profile');

async function run(){

    dotenv.config({path: `${process.env.GITHUB_WORKSPACE}/.github/.env.lambda` });

    const registryName = process.env["REGISTRY"];

    console.log(`Running docker build, image: ${registryName}`);
    exec(`docker build -t ${registryName} .`, (error, stdout, stderr) => {
        if (stderr){ core.setFailed(`docker build has failed: ${stderr}`); }
        if (error){ core.setFailed(`docker build has failed: ${error}`); }
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

    ecr.getAuthorizationToken(params, function(err, data) {
        if (err) { core.setFailed(`get auth token failed: ${err}`); }
        
        let authToken = data.authorizationData[0].authorizationToken
        let endPoint = data.authorizationData[0].proxyEndpoint.replace("https://", "")        

        console.log(`Getting login of ecr: ${endPoint}`);
        exec(`docker login -u AWS -p ${authToken} ${endPoint}`, (error, stdout, stderr) => {
            if (stderr){ core.setFailed(`docker login has failed: ${stderr}`); }
            if (error){ core.setFailed(`docker login has failed: ${error}`); }

            console.log(`docker tag ${registryName}:${imageTag} ${imageECR}`);
            exec(`docker tag ${registryName}:${imageTag} ${imageECR}`, (error, stdout, stderr) => {
                    if (stderr){ core.setFailed(`docker tag has failed: ${stderr}`); }
                    if (error){ core.setFailed(`docker tag has failed: ${error}`); }
                });

            console.log(`docker push ${imageECR}`);
            exec(`docker push ${imageECR}`, (error, stdout, stderr) => {
                    if (stderr){ core.setFailed(`docker push has failed: ${stderr}`); }
                    if (error){ core.setFailed(`docker push has failed: ${error}`); }
                });
            });

        let imageTag = process.env.GITHUB_SHA.substring(0, 8)
        let imageECR = `${endPoint}/${registryName}:${imageTag}`

        core.setOutput("image", imageECR);
        core.setOutput("repository", process.env.GITHUB_REPOSITORY.split("/")[1])

      });   

}

module.exports = run;

if (require.main === module) {
    run();
}