# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 17.05.17


import abc
import logging

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DatabaseConnection(metaclass=abc.ABCMeta):

    def __init__(self):
        self._connection = None

    def close(self):
        logger.info("Closing connection to db")
        self._connection.close()

    @abc.abstractmethod
    def query(self, q):
        pass

    @abc.abstractmethod
    def execute(self, statement):
        pass

    @abc.abstractmethod
    def insert_many(self, many, tab):
        pass

    @abc.abstractmethod
    def insert_elements(self, file, meta, f):
        pass

    @abc.abstractmethod
    def exists(self, tab):
        pass