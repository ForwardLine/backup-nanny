import logging
import sys
from troposphere.awslambda import Function, VPCConfig, Code, Environment, Permission

from buildlib.helpers.client_helper import ClientHelper


class LambdaHelper(object):

    PYTHON_RUNTIME = 'python3.7'

    def __init__(self, template=None, project=None, session=None):
        self.client = ClientHelper.get_client('lambda', session)
        self.template = template
        self.project = project

    def create_function(
        self,
        code,
        role,
        environment=None,
        memory='128',
        timeout='5',
        description='',
        handler='lambda.handler',
        name_prefix='',
        **kwargs):
        environment_variables = self.create_environment_variables(environment)
        return self.template.add_resource(Function(
            '{0}Function'.format(name_prefix),
            Runtime=self.PYTHON_RUNTIME,
            Code=code,
            Handler=handler,
            Timeout=timeout,
            MemorySize=memory,
            Description=description,
            Role=role,
            Environment=environment_variables,
            **kwargs
        ))

    @staticmethod
    def create_environment_variables(environment=None):
        if not environment:
            environment = {}
        return Environment(Variables=environment)

    def create_vpc_function(self, subnets, security_groups, **kwargs):
        vpc_config = VPCConfig(SecurityGroupIds=security_groups, SubnetIds=subnets)
        return self.create_function(VpcConfig=vpc_config, **kwargs)

    @staticmethod
    def create_bucket_code(bucket, key):
        return Code(S3Bucket=bucket, S3Key=key)

    @staticmethod
    def create_inline_code(inline_code):
        return Code(ZipFile=inline_code)

    def create_invoke_permission_for_sns(self, function_name, source_arn, name_prefix=''):
        return self.template.add_resource(Permission(
            '{0}Permission'.format(name_prefix),
            Action='lambda:InvokeFunction',
            FunctionName=function_name,
            SourceArn=source_arn,
            Principal='sns.amazonaws.com'
        ))

    def create_invoke_permission_for_events(self, function_name, source_arn, name_prefix=''):
        return self.template.add_resource(Permission(
            '{0}Permission'.format(name_prefix),
            Action='lambda:InvokeFunction',
            FunctionName=function_name,
            SourceArn=source_arn,
            Principal='events.amazonaws.com'
        ))
