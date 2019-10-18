from boto3.session import Session
import os
from sys import exit

class EmailClient(object):

    CHARSET = 'utf-8'

    def __init__(self, session=None):
        self.client = self.get_client(session)
        self.EMAILS = os.environ['TARGET_EMAILS']
        self.SOURCE_EMAIL = os.environ['SOURCE_EMAIL']
        self.ENVIRONMENT = os.environ['ENVIRONMENT']
        self.SEND_EMAILS = os.environ['IS_SEND_EMAILS_ENABLED'].upper()

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
                Source=self.SOURCE_EMAIL
            )

