from datetime import datetime
import time
from typing import List
import threading
from queue import Queue
import pickle

from polymetis import RobotInterface
from polymetis_pb2 import Empty
from data_magement.base_data_manager import BaseDataManager

class RobotDataManager(BaseDataManager):
    def __init__(self, robot: RobotInterface, log_info:str = '', store_freq:float = None, downsamling_ratio:int = 1):
        """Data manager for robot data.

        Args:
            robot (RobotInterface):         Robot interface to log data from.
            log_info (str, optional):       Information about the data to be logged. Defaults to ''.
            store_freq (float, optional):   Frequency in Hz in which to write the data to the log. 
                                            All data will always be logged. 
                                            Executes only after "Stop" or "Split" event if None. 
                                            Recommended to keep frequency low to avoid performance issues.
                                            Defaults to None.
        """
        super().__init__(log_info, store_freq)
        self.robot = robot
        self.downsampling_ratio = downsamling_ratio

    def run(self):
        start_time = datetime.now()

        stream = self.robot.grpc_connection.GetRobotStateStream(Empty())
        split_cnt = 0
        current_split = Queue()

        last_store_time = datetime.now()

        stop_update_event = threading.Event()
        def _update_queue():
            while True:
                for robot_state in stream:
                    if not stop_update_event.is_set():
                        if self.step % self.downsampling_ratio == 0:
                            current_split.put(robot_state)
                    else:
                        stop_update_event.clear()
                        return

        update_threat = threading.Thread(target=_update_queue, args=(), daemon=True)
        update_threat.start()

        while not self._stop_event.is_set():
            log_delay = None if self.store_freq is None else 1/self.store_freq * 1000 # in ms
            if self._split_event.is_set():
                self._split_event.clear()
                stop_update_event.set()
                update_threat.join()
                log_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}_{self.log_info}_SPLIT_{split_cnt}"
                store_data = list()
                while not current_split.empty():
                    store_data.append(current_split.get())
                self._store_data(store_data, log_name)
                split_cnt += 1
                current_split = Queue()
                update_threat = threading.Thread(target=_update_queue, args=(), daemon=True)
                update_threat.start()

            if log_delay is not None:
                store_data = list()
                if (datetime.now() - last_store_time).microseconds >= log_delay:
                    last_store_time = datetime.now()
                    new_data = list()
                    while not current_split.empty():
                        new_data.append(current_split.get())
                    store_data += new_data
                    log_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}_{self.log_info}_SPLIT_{split_cnt}"
                    self._store_data(store_data, log_name)
            time.sleep(0.1)
    
        self._stop_event.clear()
        stop_update_event.set()
        update_threat.join()
        log_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}_{self.log_info}_SPLIT_{split_cnt}"
        store_data = list()
        while not current_split.empty():
            store_data.append(current_split.get())
        self._store_data(store_data, log_name)
        self.logger.debug("Stopped.")
