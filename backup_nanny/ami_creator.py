#!/usr/bin/env python

from backup_nanny.util.env_loader import ENVLoader
from backup_nanny.util.log import Log
from backup_nanny.util.backup_helper import BackupHelper


def handler(event, context):
    main(event)

def main(event):
    log = Log()
    try:
        backup_helper = BackupHelper(log=log)
        instances = backup_helper.get_instances_for_ami_backup()
        for instance in instances:
            backup_helper.create_ami_backup(instance)
    except Exception as e:
        log.info(e)
        log.send_alert()
    return True

if __name__ == '__main__':
    ENVLoader.run()
    main('local')
