#!/usr/bin/env python3

import os

from troposphere import GetAtt, Ref, Join, ImportValue
from dotenv import load_dotenv
if 'CODEBUILD_BUILD_ID' not in os.environ:
    load_dotenv()

from fl_aws.helpers.template_base import TemplateBase


class BackupNanny(TemplateBase):

    PROJECT = 'BackupNanny'
    ENVIRONMENT = os.environ['ENVIRONMENT']
    PRODUCTION_ENVIRONMENT = os.environ['PRODUCTION_ENVIRONMENT']
    BACKUP_AMI_KEY = os.environ['BACKUP_AMI_KEY']
    BACKUP_AMI_VALUE = os.environ['BACKUP_AMI_VALUE']
    BACKUP_AMI_SCHEDULE_EXPRESSION = os.environ['BACKUP_AMI_SCHEDULE_EXPRESSION']
    CLEANUP_AMI_SCHEDULE_EXPRESSION = os.environ['CLEANUP_AMI_SCHEDULE_EXPRESSION']
    IS_SEND_EMAILS_ENABLED = os.environ['IS_SEND_EMAILS_ENABLED']
    TARGET_EMAILS = os.environ['TARGET_EMAILS']
    SOURCE_EMAIL = os.environ['SOURCE_EMAIL']
    TTL_AMI_CLEANUP = os.environ['TTL_AMI_CLEANUP']

    def init_template(self):

        """ Parameters """
        alert_emails = self.create_ssm_parameter(name='AlertEmailsParameter')

        """ Build variables """
        bucket = os.environ.get('APP_BUCKET', 'default-bucket-name')
        bucket_artifact = os.environ.get('ARTIFACT_NAME', 'default-bucket-name')

        """ Lambda code """
        lambda_code = self.lambda_helper.create_bucket_code(bucket=bucket, key=bucket_artifact)

        lambda_roles = []

        """--------------------
        AMI Creator
        ---------------------"""

        """ AMI Creator role """
        ami_creator_role = self.iam_helper.create_lambda_vpc_role(name_prefix='AMICreator')
        lambda_roles.append(ami_creator_role)

        ami_creator_environment_variables = {
            'EMAILS': Ref(alert_emails),
            'SEND_EMAILS': self.IS_SEND_EMAILS_ENABLED,
            'ENVIRONMENT': self.ENVIRONMENT,
            'PRODUCTION_ENVIRONMENT': self.PRODUCTION_ENVIRONMENT,
            'BACKUP_AMI_KEY': self.BACKUP_AMI_KEY,
            'BACKUP_AMI_VALUE': self.BACKUP_AMI_VALUE,
            'TTL_AMI_CLEANUP': self.TTL_AMI_CLEANUP,
            'IS_SEND_EMAILS_ENABLED': self.IS_SEND_EMAILS_ENABLED,
            'TARGET_EMAILS': self.TARGET_EMAILS,
            'SOURCE_EMAIL': self.SOURCE_EMAIL,
        }

        """ AMI Creator Lambda Function """
        ami_creator_lambda = self.lambda_helper.create_function(
            name_prefix='AMICreator',
            code=lambda_code,
            handler='ami_creator.handler',
            timeout='20', # seconds
            environment=ami_creator_environment_variables,
            role=GetAtt(ami_creator_role, 'Arn'))

        """ AMI Creator Policies """
        ami_creator_lambda_policy = self.iam_helper.create_allow_policy(
            name='AMICreatorPolicy',
            actions=['ec2:DescribeInstances', 'ec2:CreateTags', 'ec2:CreateImage', 'ec2:CreateVolume'],
            resources=['*'])
        ami_creator_policy = self.iam_helper.create_policy_roles_type(
            document=ami_creator_lambda_policy,
            roles=[Ref(ami_creator_role)],
            name_prefix='AMICreator')

        """ CloudWatch Rule with target to trigger AMI Creator Lambda """
        ami_creator_target = self.events_helper.create_target(
            arn=GetAtt(ami_creator_lambda, 'Arn'),
            target_id='AMICreatorCron')
        ami_creator_rule = self.events_helper.create_cron_rule(
            name_prefix='AMICreator',
            schedule_expression=self.BACKUP_AMI_SCHEDULE_EXPRESSION,
            targets=[ami_creator_target],
            state='ENABLED')

        """ Grant CloudWatch Rule permission to invoke AMI Creator Lambda Function """
        ami_creator_permission = self.lambda_helper.create_invoke_permission_for_events(
            function_name=Ref(ami_creator_lambda),
            source_arn=GetAtt(ami_creator_rule, 'Arn'),
            name_prefix='AMICreator')

        """--------------------
        AMI Cleanup
        ---------------------"""

        """ AMI Cleanup role """
        ami_cleanup_role = self.iam_helper.create_lambda_vpc_role(name_prefix='AMICleanup')
        lambda_roles.append(ami_cleanup_role)

        ami_cleanup_environment_variables = {
            'EMAILS': Ref(alert_emails),
            'SEND_EMAILS': self.IS_SEND_EMAILS_ENABLED,
            'ENVIRONMENT': self.ENVIRONMENT,
            'PRODUCTION_ENVIRONMENT': self.PRODUCTION_ENVIRONMENT,
            'BACKUP_AMI_KEY': self.BACKUP_AMI_KEY,
            'BACKUP_AMI_VALUE': self.BACKUP_AMI_VALUE,
            'TTL_AMI_CLEANUP': self.TTL_AMI_CLEANUP,
            'IS_SEND_EMAILS_ENABLED': self.IS_SEND_EMAILS_ENABLED,
            'TARGET_EMAILS': self.TARGET_EMAILS,
            'SOURCE_EMAIL': self.SOURCE_EMAIL,
        }

        """ AMI Cleanup Lambda Function """
        ami_cleanup_lambda = self.lambda_helper.create_function(
            name_prefix='AMICleanup',
            code=lambda_code,
            handler='ami_cleanup.handler',
            timeout='20', # seconds
            environment=ami_cleanup_environment_variables,
            role=GetAtt(ami_cleanup_role, 'Arn'))

        """ AMI Cleanup Policies """
        ami_cleanup_lambda_policy = self.iam_helper.create_allow_policy(
            name='AMICleanupPolicy',
            actions=['ec2:DeregisterImage', 'ec2:DeleteSnapshot', 'ec2:DescribeImages'],
            resources=['*'])
        ami_cleanup_policy = self.iam_helper.create_policy_roles_type(
            document=ami_cleanup_lambda_policy,
            roles=[Ref(ami_cleanup_role)],
            name_prefix='AMICleanup')

        """ CloudWatch Rule with target to trigger AMI Cleanup Lambda """
        ami_cleanup_target = self.events_helper.create_target(
            arn=GetAtt(ami_cleanup_lambda, 'Arn'),
            target_id='AMICleanupCron')
        ami_cleanup_rule = self.events_helper.create_cron_rule(
            name_prefix='AMICleanup',
            schedule_expression=self.CLEANUP_AMI_SCHEDULE_EXPRESSION,
            targets=[ami_cleanup_target],
            state='ENABLED')

        """ Grant CloudWatch Rule permission to invoke AMI Creator Lambda Function """
        ami_cleanup_permission = self.lambda_helper.create_invoke_permission_for_events(
            function_name=Ref(ami_cleanup_lambda),
            source_arn=GetAtt(ami_cleanup_rule, 'Arn'),
            name_prefix='AMICleanup')

        """-------------------
        Shared Resources
        -------------------"""

        """ Policies for SES """
        ses_lambda_policy = self.iam_helper.create_allow_policy(
            name='sesLambdaPolicy',
            actions=['ses:SendEmail', 'ses:SendRawEmail'],
            resources=['*'])
        self.iam_helper.create_policy_roles_type(
            document=ses_lambda_policy,
            roles=[Ref(role) for role in lambda_roles],
            name_prefix='SES')


if __name__ == '__main__':
    backup_nanny = BackupNanny()
    backup_nanny.init_template()
    print(backup_nanny.t.to_json())
