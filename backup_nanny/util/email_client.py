from boto3.session import Session
import os
from sys import exit

class EmailClient(object):

    EMAILS = os.environ['EMAILS']
    ENVIRONMENT = os.environ['ENVIRONMENT']
    SEND_EMAILS = os.environ['SEND_EMAILS'].upper()
    CHARSET = 'utf-8'

    def __init__(self, session=None):
        self.client = self.get_client(session)

    def get_client(self, session=None):
        if not session:
            session = Session()
        return session.client('ses')

    def alert(self, message):
        if self.SEND_EMAILS == 'TRUE':
            return self.client.send_email(
                Destination={
                    'ToAddresses': [email for email in self.EMAILS.split(',')],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': self.CHARSET,
                            'Data': 'BackupNanny {0} has experienced an issue. The app log recorded is: <br/><br/>{1}'.format(self.ENVIRONMENT, message),
                        },
                    },
                    'Subject': {
                        'Charset': self.CHARSET,
                        'Data': 'BackupNanny {0} alert'.format(self.ENVIRONMENT),
                    },
                },
                Source='no-reply@forwardline.com'
            )

