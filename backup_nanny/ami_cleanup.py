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
        backup_amis = backup_helper.get_backup_amis_for_cleanup()
        for backup_ami in backup_amis:
            backup_helper.cleanup_old_ami(backup_ami)
            backup_helper.cleanup_old_snapshots(backup_ami.snapshots)
    except Exception as e:
        log.info(e)
        log.send_alert()
    return True

if __name__ == '__main__':
    ENVLoader.run()
    main('local')
