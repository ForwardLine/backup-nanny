import logging
from troposphere import Ref, Join
from troposphere.iam import Group, PolicyType, Role, User
from awacs.aws import Action, Allow, Policy, Statement, Deny, Condition, Null, Principal, AWSPrincipal
from awacs.sts import AssumeRole
from awacs.helpers import trust

from buildlib.helpers.client_helper import ClientHelper


class IAMHelper(object):

    IAM_ARN = 'arn:aws:iam::'

    def __init__(self, template=None, project=None, session=None):
        self.client = ClientHelper.get_client('iam', session)
        self.template = template
        self.project = project

    def create_role(self, service, name_prefix='', **kwargs):
        return self.template.add_resource(Role(
            '{0}Role'.format(name_prefix),
            AssumeRolePolicyDocument=self.get_role(service),
            **kwargs
        ))

    def get_role(self, service_name):
        service = '{0}.amazonaws.com'.format(service_name)
        return trust.make_simple_assume_policy(service)

    def create_lambda_role(self, name_prefix='', **kwargs):
        lambda_role = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        return self.create_role(service='lambda',
            name_prefix=name_prefix,
            ManagedPolicyArns=[lambda_role],
            **kwargs)


    def create_policy_roles_type(self, document, roles, name_prefix=''):
        return self._create_policy_type(
            document=document,
            Roles=roles,
            name_prefix=name_prefix)

    def _create_policy_type(self, document, name_prefix='', **kwargs):
        return self.template.add_resource(PolicyType(
            '{0}Policy'.format(name_prefix),
            PolicyName='{0}{1}Policy'.format(self.project, name_prefix),
            PolicyDocument=document,
            **kwargs))

    def create_allow_policy(self, name, actions, resources):
        awacs_actions = [Action(action.split(':')[0], action.split(':')[1]) for action in actions]
        return Policy(
            Version='2012-10-17',
            Id='{0}{1}'.format(self.project, name),
            Statement=[
                Statement(
                    Effect=Allow,
                    Action=awacs_actions,
                    Resource=resources
                )
            ]
        )



