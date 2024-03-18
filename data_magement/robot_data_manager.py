from datetime import datetime
import time

from polymetis import RobotInterface
from data_magement.base_data_manager import BaseDataManager

class RobotDataManager(BaseDataManager):
    def __init__(self, robot: RobotInterface, log_info:str = '', store_freq:float = None):
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

    def run(self):
        start_time = datetime.now()

        robot_interval = self.robot.get_previous_interval()
        robot_log = self.robot.get_previous_log()
        robot_interval.start += len(robot_log)
        robot_interval.end = -1
        split_cnt = 0
        current_split = list()

        last_store_time = datetime.now()

        while not self._stop_event.is_set():
            log_delay = None if self.store_freq is None else 1/self.store_freq * 1000 # in ms
            if self._split_event.is_set():
                self._split_event.clear()
                current_split += self.robot._get_robot_state_log(robot_interval)
                log_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}_{self.log_info}_SPLIT_{split_cnt}"
                self._store_data(current_split, log_name)
                split_cnt += 1
                current_split = list()

            if log_delay is not None:
                if (datetime.now() - last_store_time).microseconds >= log_delay:
                    last_store_time = datetime.now()
                    new_data = self.robot._get_robot_state_log(robot_interval)
                    robot_interval.start += len(new_data)
                    current_split += new_data
                    log_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}_{self.log_info}_SPLIT_{split_cnt}"
                    self._store_data(current_split, log_name)
            
            time.sleep(0.1)
    
        self._stop_event.clear()
        current_split += self.robot._get_robot_state_log(robot_interval)
        log_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}_{self.log_info}_SPLIT_{split_cnt}"
        self._store_data(current_split, log_name)
        self.logger.debug("Stopped.")