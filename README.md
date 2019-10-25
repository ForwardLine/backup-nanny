# BackupNanny
A series of Lambda functions that are used to automate AWS backups

## Details
Allows one to manage (create and cleanup) backups of EC2 images and associated volume snapshots by tagging resources.
The tool is flexible and all parts of it are customizable via a configuration file used during deployment.
Easily deploy one or many BackupNanny environments across your AWS account(s). Each one can be customized to make/delete backups at specified frequencies for specific tags you configure.

### Advantages of using this:
- Open source
- flexible/customizable (user can deploy one or many environments, each running at different frequences, each targetting different tags, each with different TTL of resources they manage)
- Stable (AWS resources managed in CloudFormation via code)
- Ships with a CI/CD environment (managed via code) per deployment of BackupNanny (easy/stable way to apply changes when updates occur and/or enhancements made)
- Serverless (Lambda functions are used, triggered in cron fashion by Cloudwatch Event Rules. CI/CD is also Serverless)
- Command line tool that easily deploys the application once config file has been saved in correct location with necessary values.

## BackupNanny Functions
- AMICreator: Filters for EC2 instances you have tagged in a specific way (that you chose) and generates an Amazon Machine Image (AMI). AMIs include snapshots of any volumes that were attached to the instance(s). Runs at a frequency you choose.
- AMICleanup: Filters for AMIs and volumes that BackupNanny has created via the AMICreator Lambda function. If these resuorces are older than you specified the Time to Live (TTL) in the config, then we delete those resources here. Runs at a frequence you choose.

## Setup
Whether you are looking to deploy BackupNanny, test it out locally first, have a cool idea to implement, and/or want to get your open-source points in, this is a good place to start!

This guide assumes you have Python, pip, and virtualenv installed locally.
Also it assumes you are set up locally to use AWS via ~/.aws/credentials.
Please view this for reference:
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file

- Fork the repository
- git clone to local machine
- Activate virtual environment

```
# If you do not have virtualenv installed, install it!
pip install virtualenv

# If you do not have a virtualenv, make it. We use Python3
virtualenv -p $(which python3) venv

# Activate the venv
. venv/bin/activate
```
- Install the dependencies
```
python setup.py install
```

## Deploying
BackupNanny comes with a deployment tool that will provision CI/CD for each environment of BackupNanny.
AWS CodePipeline is used to manage CI/CD for this project.
You may deploy as many versions of BackupNanny as rules you have for backing up your resources.
Environments you deem to be non-production (within the config file) will be considered a "test" environment. Any boto3 commands in a test environment will make boto3 commands using the --dry-run option (no resources will be generated or deleted)

First, ensure you have completed the steps found in the "Setup" section above.

Next, create a direcory called `.backup-nanny` in ~ ($HOME path) and copy the .env file in the root of this repo there.
You should end up with a file and path such as:
`~/.backup-nanny/.env`

Now open the .env file within ~/.backup-nanny and update this config file using your values.
Config file has descriptions for each of the values and their use-cases.

To deploy a "production" environment of BackupNanny (where AMIs and Volumes get generated/deleted), ensure the ENVIRONMENT and PRODUCTION_ENVIRONMENT values are the same, case-insensitive.

Once you have filled out all of the values, run the following command:
```
deploy
```

If this completes successfully, you will have a CodePipeline that will start trying to build and deploy your environment of BackupNanny!

There are a few reasons why this may fail:
1. You do not have an AWS token and secret set up properly
2. Your access token does not provide you necessary permissions
3. You did not add the .env credentials to the correct location
4. You did not fill out the credentials correctly.
5. The PAT variable you used does not have necessar permission in your Github account (Repo, read:repo_hook, and admin:org_hook)

## CI/CD
Upon completion of the Pipeline, the environment of BackupNanny that you deployed will be live!
You will see the lambda functions in the Lambda service of AWS.
You will see the Cloudwatch Event Rules in the Cloudwatch service of AWS.

The CodePipeline and CodeBuild resources are managed within the `buildlib/pipeline.json` file found in the buildlib directory within root of the project.
The steps that CodeBuild takes are found within the `buildlib/buildspec.yml` file.

The automation is currently the same per environment (test or production), and looks like like this when a merge to one of the two branches above happens:
* Source
  * Webhook from Github triggers Pipeline source to pick up the latest commit of that branch
* CodeBuild
  * Runs the unit tests
  * Creates the artifacts and uploads them to necessary locations in S3
  * buildspec.yml in the buildlib directory manages what steps CodeBuild takes
* Changeset
  * the artifact generated in the CodeBuild step is used to form a CloudFormation Changeset, showing the changes the recent commit will have on that environment
* Deploy
  * Once the Changeset is successfully created, it is executed. This safely applies the changes using CloudFormation. Failures will automatically roll the environment back to the last stable state.

There are a few reasons why the pipeline may fail:
1. BRANCH variable you set is not an actual branch in your forked backup-nanny repository
2. Other variables you set in `.env` file within `~/.backup-nanny` are not correctly set

## Unit Tests
We are using the unittest module for writing unit tests
We use module nose to run the unit tests

To run the unit tests:
```
# Ensure you are in your venv first and have completed "Setup" section above
python setup.py nosetests
```

To run unit tests and view code coverage:
```
python setup.py coverage
```

## AWS Resources
The AWS resources (Lambda Functions, CloudWatch Event Rules) are managed via CloudFormation.
The template is generated via Troposphere.
Troposphere code is found within the file:
`buildlib/infrastructure.py`

To test the AWS resources CloudFormation creation step, please ensure you first have gone through the "Setup" section above:
```
python -m buildlib.infrastructure
```

## Application code
Found within the backup_nanny directory

```
Braverman@Local ~/Repos/backup-nanny/backup_nanny $ tree -I __pycache__
.
├── ami_cleanup.py
├── ami_creator.py
├── builder
├── requirements.txt
└── util
    ├── ...
```

## Monitoring
AWS CloudWatch is used to centrally store logs from Lambda Functions.

## Notifications
If you enabled the `IS_SEND_EMAILS_ENABLED` flag, problems that occur will notify to users in the `TARGET_EMAILS` variable and are sent from the `SOURCE_EMAIL` email address.
Please ensure you have verified the email address you choose to send as, and are outside of the SES sandbox environment:
https://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html

