from boto3.session import Session
from sys import exit

class LambdaClient(object):

    def __init__(self, session=None):
        self.client = self.get_client(session)

    def get_client(self, session=None):
        if not session:
            session = Session()
        return session.client('lambda')

    def invoke(self, name, payload, invocation_type='Event'):
        return self.client.invoke(
            FunctionName=name,
            InvocationType=invocation_type,
            Payload=payload)

