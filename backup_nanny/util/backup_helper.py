import os
from datetime import datetime

from botocore.exceptions import ClientError

from backup_nanny.util.client_helper import ClientHelper
from backup_nanny.util.instance_reservation import InstanceReservation
from backup_nanny.util.image import Image


class BackupHelper(object):


    def __init__(self, log):
        self.ec2_client = ClientHelper.get_client('ec2')
        self.log = log
        self.BACKUP_AMI_KEYS = [os.environ['BACKUP_AMI_KEY']]
        self.BACKUP_AMI_VALUES = [os.environ['BACKUP_AMI_VALUE']]
        self.PRODUCTION_ENVIRONMENT = os.environ['PRODUCTION_ENVIRONMENT']
        self.ENVIRONMENT = os.environ.get('ENVIRONMENT', 'LOCAL')
        self.dry_run = self.is_dry_run()

    def get_instances_for_ami_backup(self):
        instances = []
        try:
            reservations_for_backup = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'tag-key', 'Values': self.BACKUP_AMI_KEYS},
                    {'Name': 'tag-value', 'Values': self.BACKUP_AMI_VALUES}
                ]
            )['Reservations']
            self.log.info('found {0} instances tagged for ami-backup'.format(len(reservations_for_backup)))
            for reservation in reservations_for_backup:
                instance = InstanceReservation(reservation_info=reservation)
                self.log.info('Will backup: {0} ({1})'.format(instance.name, instance.instance_id))
                instances.append(instance)
        except Exception as e:
            self.log.info('there was an error in the "get_instances_for_ami_backup" method. Returning empty list')
            self.log.info(e)
        return instances

    def get_backup_amis_for_cleanup(self):
        try:
            cleanup_images = []
            aws_images = self.ec2_client.describe_images(
                Filters=[
                    {'Name': 'tag-key', 'Values': self.BACKUP_AMI_KEYS},
                    {'Name': 'tag-value', 'Values': self.BACKUP_AMI_VALUES}
                ]
            )['Images']
            self.log.info('found {0} images tagged for ami-backup'.format(len(aws_images)))
            for aws_image in aws_images:
                image = Image(image_info=aws_image)
                self.log.info('Image "{0}" ({1}) has creation date of {2}'.format(image.name, image.image_id, image.creation_date))
                image_creation_datetime = datetime.strptime(image.creation_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                time_since_now = datetime.now() - image_creation_datetime
                if time_since_now.days > image.ttl_days:
                    cleanup_images.append(image)
                    self.log.info('Image "{0}" ({1}) along with snapshots {2} will be deleted as it was created over {3} days ago'.format(image.name, image.image_id, image.snapshots, image.ttl_days))
                else:
                    self.log.info('Image "{0}" ({1}) will not be deleted as it was not created over {2} days ago'.format(image.name, image.image_id, image.ttl_days))
        except Exception as e:
            self.log.info('there was an error in the "get_backup_amis_for_cleanup" method. Returning empty list')
            self.log.info(e)
        return cleanup_images

    def cleanup_old_ami(self, image):
        try:
            self.log.info('Deleting AMI for {0} ({1})'.format(image.name, image.image_id))
            self.ec2_client.deregister_image(ImageId=image.image_id, DryRun=self.dry_run)
            self.log.info('Deleted AMI for {0} ({1})'.format(image.name, image.image_id))
        except ClientError as ce:
            if ce.response['Error']['Code'] == 'DryRunOperation':
                self.log.info('DryRun is enabled, no image deleted')
            else:
                self.log.info(ce)
        except Exception as e:
            self.log.info('failed to delete AMI {0} ({1})'.format(image.name, image.image_id))
            self.log.info(e)

    def cleanup_old_snapshots(self, snapshots):
        for snapshot in snapshots:
            try:
                self.log.info('Deleting snapshot {0}'.format(snapshot))
                self.ec2_client.delete_snapshot(SnapshotId=snapshot, DryRun=self.dry_run)
                self.log.info('Deleted snapshot {0}'.format(snapshot))
            except ClientError as ce:
                if ce.response['Error']['Code'] == 'DryRunOperation':
                    self.log.info('DryRun is enabled, snapshot not deleted')
                else:
                    self.log.info(ce)
            except Exception as e:
                self.log.info('failed to delete snapshot {0}'.format(snapshot))
                self.log.info(e)

    def create_ami_backup(self, instance):
        try:
            date = datetime.now().strftime('%Y.%m.%d')
            self.log.info('Creating AMI for {0} ({1})'.format(instance.name, instance.instance_id))
            image = self.ec2_client.create_image(
                DryRun=self.dry_run,
                Description="BackupNanny - created via automated process. EC2 instance has {0} label set to {1}".format(os.environ['BACKUP_AMI_KEY'], os.environ['BACKUP_AMI_VALUE']),
                InstanceId=instance.instance_id,
                Name='--'.join([instance.name, date]),
                NoReboot=True)
            self.log.info('Created AMI ({2}) for {0} ({1})'.format(instance.name, instance.instance_id, image['ImageId']))
            self.ec2_client.create_tags(
                DryRun=self.dry_run,
                Resources=[image['ImageId']],
                Tags=[{'Key': self.BACKUP_AMI_KEYS[0], 'Value': self.BACKUP_AMI_VALUES[0]}])
            self.log.info('Tagged AMI {0}'.format(image['ImageId']))
        except ClientError as ce:
            if ce.response['Error']['Code'] == 'DryRunOperation':
                self.log.info('DryRun is enabled, no image created')
            else:
                self.log.info(ce)
        except Exception as e:
            self.log.info('failed to create AMI for {0} ({1})'.format(instance.name, instance.instance_id))
            self.log.info(e)

    def is_dry_run(self):
        return True if not self.ENVIRONMENT or self.ENVIRONMENT.upper() not in self.PRODUCTION_ENVIRONMENT.upper() else False

