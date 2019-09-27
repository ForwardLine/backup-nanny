from os import environ as env

from boto3.session import Session


class EnvSetter(object):
    SSM_KEYS = []

    @staticmethod
    def run():
        session = Session()
        client = session.client('ssm')
        parameter_values = []
        if EnvSetter.SSM_KEYS:
            parameter_values = client.get_parameters(Names=EnvSetter.SSM_KEYS, WithDecryption=True)['Parameters']
        for parameter_value in parameter_values:
            env.update({parameter_value['Name'].split('/')[-1]: parameter_value['Value']})
