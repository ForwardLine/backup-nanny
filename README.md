# BackupNanny 
this is a series of Lambda functions that are used to automate AWS backups 

## BackupNanny Functions
- AMICreator: 
- AMICleanup: 

## Making changes
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

## Unit Tests
We are using the unittest module for writing unit tests
We use module nose to run the unit tests

To run the unit tests:
```
# Ensure you are in your venv first and have compelted "Making Changes" step above
python setup.py nosetests
```

To run unit tests and view code coverage:
```
# Ensure you are in your venv first and have completed "Making Changes" step above
python setup.py coverage
```


## AWS Resources
The AWS resources (Lambda Functions, CloudWatch Event Rules) are managed via CloudFormation.
The template is generated via Troposphere.
Troposphere code is found within the file:
`infrastructure.py`

[fl-aws](https://github.com/ForwardLine/fl-aws) repository is used for default VPC blueprint

To test the AWS resources CloudFormation creation step, please ensure you first have gone through the Making Changes step above:
```
pip install -r infra-requirements.txt
ENVIRONMENT=STG python infrastructure.py
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

## Deploying
AWS CodePipeline is used to manage CI/CD for this project.
There are two environments: STG & PRD
STG environment will make boto3 commands using the --dry-run option

The CodePipeline and CodeBuild resources are managed within the `pipeline.json` file found in the buildlib director within root of the project.

Merging changes to two distinct branches will cause for the automation to begin.

STG: [release](https://github.com/ForwardLine/opportunity-feeder/tree/release)
PRD: [master](https://github.com/ForwardLine/opportunity-feeder/tree/master)

The automation is currently the same per environment, and looks like like this when a merge to one of the two branches above happens:
* Source
  * Webhook from Github triggers Pipeline source to pick up the latest commit of that branch
* CodeBuild
  * Creates the artifacts and uploads them to necessary locations
  * buildspec.yml in the buildlib direcgory of the root of this project manages the steps that CodeBuild takes
* Changeset
  * the artifact generated in the CodeBuild step is used to form a CloudFormation Changeset, showing the changes the recent commit will have on that environment
* Deploy
  * Once the Changeset is successfully created, it is executed. This safely applies the changes using CloudFormation. Failures will automatically roll the environment back to the last stable state.

## Monitoring
AWS CloudWatch is used to centrally store logs from Lambda Functions.

## Secret Management
AWS Parameter Store is being used to store sensitive information/credentials
Lambda functions have necessary permissions to decrypt data found within the Parameter Store during runtime


