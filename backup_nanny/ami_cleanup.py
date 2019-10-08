from util.env_setter import EnvSetter
EnvSetter.run()

from util.log import Log
from util.backup_helper import BackupHelper


def handler(event, context):
    main(event)

def main(event):
    try:
        log = Log()
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
    main('local')
