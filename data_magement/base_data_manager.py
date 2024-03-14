import threading
import logging
import h5py
import os

import abc

class BaseDataManager(threading.Thread, abc.ABC):
    def __init__(self, log_info:str = '', store_freq:float = 0.5):
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

    def _store_data(self, data, log_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "data")
        log_file_path = os.path.join(data_dir, f"{log_name}.h5")
        with h5py.File(log_file_path, 'w') as f:
            for key, value in data.items():
                f.create_dataset(key, data=value)