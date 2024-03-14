from datetime import datetime

from polymetis import RobotInterface
from data_magement.base_data_manager import BaseDataManager

class RobotDataManager(BaseDataManager):
    def init__(self, robot: RobotInterface, log_info:str = '', store_freq:float = 0.5):
        super().__init__(log_info, store_freq)
        self.robot = robot

    def run(self):
        start_time = datetime.now()
        robot_timestamp_current = self.robot.get_robot_state()["timestamp"]
        interval_start = robot_timestamp_current
        current_split = list()
        split_cnt = 0
        while not self._stop_event.is_set():
            log_delay = 1/self.store_freq * 1000 # in ms
            robot_timestamp_current = self.robot.get_robot_state()["timestamp"]
            if self._split_event.is_set():
                self._split_event.clear()
                log_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}_{self.log_info}_SPLIT_{split_cnt}"
                self._store_data(current_split, log_name)
                split_cnt += 1
                interval_start = robot_timestamp_current
                current_split = list()
            if robot_timestamp_current >= interval_start + log_delay:
                current_split += self.robot._get_robot_state_log((interval_start, robot_timestamp_current))
                log_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}_{self.log_info}_SPLIT_{split_cnt}"
                self._store_data(current_split, log_name)