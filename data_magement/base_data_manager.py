import threading
import logging

import abc

class BaseDataManager(threading.Thread, abc.ABC):
    def __init__(self, log_info:str = '', store_freq:float = '0.5'):
        super().__init__()
        self.logger = logging.Logger(__name__)
        self._stop_event = threading.Event()
        self._split_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        self.logger.debug("Stop event set.")

    def split(self):
        self._split_event.set()
        self.logger.debug("Split event set.")