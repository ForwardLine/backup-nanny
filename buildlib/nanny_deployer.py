import os
import logging
import json

from buildlib.helpers.cloudformation_helper import CloudformationHelper
from buildlib.helpers.parameter import Parameter


class NannyDeployer(object):

    def __init__(self, stack_name, region, use_previous_value=False, session=None):
        self.use_previous_value = use_previous_value
        self.stack_name = stack_name
        self.region = region
        self.template_json = None
        self.parameters = None
        self.cloudformation_helper = CloudformationHelper(session=session)

    def deploy(self):
        with open('buildlib/pipeline.json', 'r') as fb:
            self.template_json = fb.read()
        self.parameters = json.loads(self.template_json)['Parameters'].keys()
        self.create_or_update_stack()

    def create_or_update_stack(self):
        if self.cloudformation_helper.get_stack_info(stack_name=self.stack_name):
            logging.info('Use previous value is set to: {0}'.format(self.use_previous_value))
            parameters = self.get_parameters(use_previous_value=self.use_previous_value)
            self.cloudformation_helper.update_stack(stack_name=self.stack_name, template_body=self.template_json, parameters=parameters)
        else:
            parameters = self.get_parameters(use_previous_value=False)
            self.cloudformation_helper.create_stack(self.stack_name, self.template_json, parameters)
        self.cloudformation_helper.stack_was_created_successfully(stack_name=self.stack_name)

    def get_parameters(self, use_previous_value):
        parameters = []
        for parameter in self.parameters:
            parameter_obj = Parameter(parameter, use_previous_value)
            if parameter_obj.has_environment_variable():
                parameters.append(parameter_obj)
        return [parameter.get_dictionary() for parameter in parameters]

