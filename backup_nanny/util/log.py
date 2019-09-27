#!/usr/bin/env python

import sys

from util.email_client import EmailClient


class Log(object):

    def __init__(self):
        self.app_log = []
        self.email_client = EmailClient()

    def info(self, message):
        print(message)
        self.app_log.append(message)

    def send_alert(self):
        self.email_client.alert(self.get_app_log(delimiter='<br/>'))

    def get_app_log(self, delimiter='\n'):
        return '<br/>'.join(str(item) for item in self.app_log)


