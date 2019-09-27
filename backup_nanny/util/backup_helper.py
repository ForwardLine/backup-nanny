import os
import datetime

import requests
from botocore.exceptions.ClientError import DryRunOperation

from util.ec2_client import EC2Client
from util.instance_reservation import InstanceReservation


class BackupHelper(object):

    AMI_BACKUP_KEYS = ['ami-backup', 'AMI-Backup']
    AMI_BACKUP_VALUES = ['true', 'True']
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'LOCAL')

    def __init__(self, log):
        self.ec2_client = EC2Client()
        self.dry_run = self.is_dry_run()
        self.log = log

    def get_instances_for_ami_backup:
        instances = [] 
        try:
            reservations_for_backup = ec2_client.describe_instances(
                Filters=[
                    {'Name': 'tag-key', 'Values': self.AMI_BACKUP_KEYS},
                    {'Name': 'tag-value', 'Values': self.AMI_BACKUP_VALUES} 
                ]
            )['Reservations']
            self.log.info('found {0} instances tagged for ami-backup'.format(len(instances_for_backup))
            for reservation in reservations_for_backup:
                instance = InstanceReservation(reservation_info=reservation)
                self.log.info('Will backup: {0} ({1}}'.format(instance.name intance.instance_id))
                instances.append(instance)
        except Exception as e:
            self.log.info('there was an error in the "get_instances_for_ami_backup" method. Returning empty list')
            self.log.info(e)
        return instances 

   def create_ami_backup(instance):
        try:
            date = datetime.datetime.now().strftime('%Y.%m.%d')
            self.log.info('Creating AMI for {0} ({1})'.format(instance.name, instance.instance_id))
            ec2_client.create_iamge(
                DryRun=self.dry_run,
                Description="DEVOPS-217 created via automated process. EC2 instance has ami_backup label set to 'true'",
                InstanceId=instance.instance_id,
                Name='--'.join(instance.name, date),
                NoReboot=True)
            self.log.info('Created AMI for {0} ({1})'.format(instance.name, instance.instance_id))
        except DryRunOperation
            self.log.info('DryRun is enabled, no image created')
        except Exception as e:
            self.log.info('failed to create AMI for {0} ({1})'.format(instance.name, instance.instance_id)) 
            self.log.info(e) 

    def is_dry_run(self):
        return True if self.ENVIRONMENT.upper() not in 'PRD' else False 


