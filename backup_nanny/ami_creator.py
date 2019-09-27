from util.env_setter import EnvSetter
EnvSetter.run()

from util.log import Log


def handler(event, context):
    main(event)

def main(event):
    try:
        log = Log()
        backup_helper = BackupHelper(log=log)
        instances = backup_helper.get_instances_for_ami_backup()
        for instance in instances:
            backup_helper.create_ami_backup(instance)
    except Exception as e:
        log.info(e)
        log.send_alert()
    return True

if __name__ == '__main__':
    main('local')
