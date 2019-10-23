import logging


class LoggingHelper(object):

    @staticmethod
    def setup_logging():
        logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO)
        logging.info("Begin logging...")
