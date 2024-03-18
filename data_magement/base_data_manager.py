import threading
import logging
import os
import pickle

import abc

class BaseDataManager(threading.Thread, abc.ABC):
    def __init__(self, log_info:str = '', store_freq:float = None):
        """Base class for data management.

        Args:
            log_info (str, optional):       Information about the data to be logged. Defaults to ''.
            store_freq (float, optional):   Frequency in Hz in which to write the data to the log. 
                                            All data will always be logged. 
                                            Executes only after "Stop" or "Split" event if None. 
                                            Recommended to keep frequency low to avoid performance issues.
                                            Defaults to None.
        """
        super().__init__()
        self.logger = logging.Logger(__name__)
        self._stop_event = threading.Event()
        self._split_event = threading.Event()
        self.log_info = log_info
        self.store_freq = store_freq

    def stop(self):
        self._stop_event.set()
        self.logger.debug("Stop event set.")

    def split(self):
        self._split_event.set()
        self.logger.debug("Split event set.")

    def _store_data(self, data, log_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "data")
        log_file_path = os.path.join(data_dir, f"{log_name}.pkl")
        with open(log_file_path, 'wb') as f:
            pickle.dump(data, f)