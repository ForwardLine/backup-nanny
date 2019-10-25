import unittest
import sys
import os


from backup_nanny.util.env_loader import ENVLoader
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = '{0}/../env_files/basic.env'.format(dir_path)
ENVLoader.run(file_path=file_path)

from backup_nanny.util.log import Log
from backup_nanny.util.backup_helper import BackupHelper

class BackupHelperTest(unittest.TestCase):

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = '{0}/../env_files/basic.env'.format(dir_path)
        ENVLoader.run(file_path=file_path)
        log = Log()
        self.backup_helper = BackupHelper(log=log)

    def test_dry_run_is_true(self):
        is_dry_run = self.backup_helper.is_dry_run()
        self.assertEqual(is_dry_run, True)

    def test_dry_run_is_false(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = '{0}/../env_files/prd.env'.format(dir_path)
        ENVLoader.run(file_path=file_path)
        prd_backup_helper = BackupHelper(log=Log())
        is_dry_run = prd_backup_helper.is_dry_run()
        self.assertEqual(is_dry_run, False)

    def test_dry_run_is_true_when_env_is_blank_in_config(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = '{0}/../env_files/blank_env.env'.format(dir_path)
        ENVLoader.run(file_path=file_path)
        prd_backup_helper = BackupHelper(log=Log())
        is_dry_run = prd_backup_helper.is_dry_run()
        self.assertEqual(is_dry_run, True)





if __name__ == '__main__':
    unittest.main()
