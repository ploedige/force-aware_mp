import threading
import logging

from polymetis import RobotInterface
from data_magement.base_data_manager import BaseDataManager

class RobotDataManager(BaseDataManager):
    def init__(self, robot: RobotInterface, log_info:str = '', store_freq:float = '0.5'):
        super().__init__(log_info, store_freq)
        self.robot = robot

    def run(self):
        raise NotImplementedError