import os

from dotenv import load_dotenv

class ENVLoader(object):

    @staticmethod
    def run(file_path='{0}/.backup-nanny/.env'.format(os.environ.get('HOME', '')), override=True):
        load_dotenv(dotenv_path=file_path, override=override)


