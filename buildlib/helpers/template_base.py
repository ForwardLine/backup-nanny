#!/usr/bin/env python3
from troposphere import Template, Parameter, Output, Export
import os
from dotenv import load_dotenv
if 'CODEBUILD_BUILD_ID' not in os.environ:
    load_dotenv()

from buildlib.helpers.iam import IAMHelper
from buildlib.helpers.awslambda import LambdaHelper
from buildlib.helpers.events import EventsHelper


class TemplateBase(object):

    STACK_NAME = os.environ['STACK_NAME']

    def __init__(self, template=None, session=None):
        self.t = template if template else Template()
        if not template:
            self.t.add_description('Stack template: {0}'.format(self.__class__.__name__))
        self.helper_params = {'template': self.t, 'project': self.PROJECT, 'session': session}
        self.iam_helper = IAMHelper(**self.helper_params)
        self.lambda_helper = LambdaHelper(**self.helper_params)
        self.events_helper = EventsHelper(**self.helper_params)

    def to_json(self):
        return self.t.to_json()
