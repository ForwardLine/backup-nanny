
from boto3.session import Session


class ClientHelper(object):

    @staticmethod
    def get_client(client_type='cloudformation', session=None, **session_args):
        if not session:
            session = Session(**session_args)
        return session.client(client_type)
