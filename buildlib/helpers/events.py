import logging
from troposphere.events import Rule, Target

from buildlib.helpers.client_helper import ClientHelper


class EventsHelper(object):

    def __init__(self, template, project, session=None):
        self.client = ClientHelper.get_client('events', session)
        self.project = project
        self.template = template

    def create_cron_rule(self, schedule_expression, targets, state='ENABLED', name_prefix='', **kwargs):
        return self.template.add_resource(Rule(
            '{0}Rule'.format(name_prefix),
            State=state,
            Targets=targets,
            ScheduleExpression=schedule_expression,
            **kwargs
        ))

    def create_target(self, arn, target_id, name_prefix=''):
        return Target(
            '{0}Target'.format(name_prefix),
            Arn=arn,
            Id=target_id
        )
