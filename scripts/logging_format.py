import logging

formatter = {
    1: logging.Formatter("%(message)s"),
    2: logging.Formatter("%(levelname)s - %(message)s"),
    3: logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"),
    4: logging.Formatter("%(asctime)s - %(levelname)s - %(message)s - [%(name)s]"),
    5: logging.Formatter("%(asctime)s - %(levelname)s - %(message)s - [%(name)s:%(lineno)s]"),
}


class Logger(object):

    def __init__(self, logname, loglevel, callfile):
        self.logger = logging.getLogger(callfile)
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler()
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        ch.setFormatter(formatter[int(loglevel)])
        fh.setFormatter(formatter[int(loglevel)])
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    def get_logger(self):
        return self.logger


if __name__ == '__main__':
    logger = Logger(logname='test', loglevel=1, callfile=__file__).get_logger()
