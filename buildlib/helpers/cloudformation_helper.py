import logging
from sys import exit
import time

from buildlib.helpers.client_helper import ClientHelper


class CloudformationHelper(object):

    FAILED_STATES = ['CREATE_FAILED', 'DELETE_FAILED', 'DELETE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']
    COMPLETE_STATES = ['CREATE_COMPLETE', 'UPDATE_COMPLETE']

    def __init__(self, template='', region=None, session=None):
        self.client = ClientHelper.get_client(client_type='cloudformation',session=session, region_name=region)
        self.template = template
        self.is_creating = False

    def get_resource_from_stack(self, resource, stack):
        return self.client.describe_stack_resource(
            StackName=stack,
            LogicalResourceId=resource
        )['StackResourceDetail']

    def get_stack_info(self, stack_name):
        try:
            return self.client.describe_stacks(StackName=stack_name)['Stacks'][0]
        except Exception as e:
            logging.info('stack info not found for: {0}'.format(stack_name))
            logging.debug(e)
            return False

    def validate_template(self, template_body):
        logging.info('Validating template')
        try:
            self.client.validate_template(TemplateBody=template_body)
        except Exception as e:
            logging.error('stack validation error', e)
            exit()

    def create_stack(self, stack_name, template_body, parameters=None):
        logging.info('Creating stack: {0}'.format(stack_name))
        stack_parameters = {}
        if parameters:
            stack_parameters = {'Parameters': parameters}
        try:
            self.client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                OnFailure='DELETE',
                Capabilities=['CAPABILITY_IAM'],
                **stack_parameters
            )['StackId']
            self.is_creating = True
        except Exception as e:
            logging.error('Failed to create stack {0}'.format(stack_name), e)
            exit()

    def update_stack(self, stack_name, template_body, parameters=None):
        logging.info('Updating stack: {0}'.format(stack_name))
        stack_parameters = {}
        if parameters:
            stack_parameters = {'Parameters': parameters}
        try:
            self.client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_IAM'],
                **stack_parameters
            )['StackId']
            self.is_creating = True
        except Exception as e:
            logging.error('Failed to update stack {0}'.format(stack_name), e)
            exit()

    def stack_was_created_successfully(self, stack_name, attempt=1, sleep_time=20):
        if attempt > 25:
            logging.info('Stack was not created/updated in the alotted time')
            return False
        try:
            stack_info = self.get_stack_info(stack_name)
            if not stack_info and self.is_creating:
                return False
            stack_status = stack_info['StackStatus']
            if stack_status in self.COMPLETE_STATES:
                logging.info('Stack has been successfully updated/created')
                return True
            if stack_status in self.FAILED_STATES:
                return False
        except Exception as e:
            logging.info('There was a problem checking status of stack: {0}'.format(e))
        logging.info('Stack creation/update still in progress. Waiting {0} seconds'.format(sleep_time))
        time.sleep(sleep_time)
        return self.stack_was_created_successfully(stack_name, attempt+1)
