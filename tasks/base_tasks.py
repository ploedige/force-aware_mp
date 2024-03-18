from abc import ABC, abstractmethod
from typing import List, Dict
import threading
import logging
import torch

from polymetis import RobotInterface

class BaseTask(threading.Thread, ABC):
    def __init__(self, robots: List[RobotInterface]) -> None:
        """Base class for tasks controlling robots in a Polymetis environment

            There are two ways to specify the task: 
            1. by passing a callable object to the constructor
            2. by overriding the run() method in a subclass.

        Args:
            robots (List[RobotInterface]): robots that can be controlled by the task
        """
        super().__init__()
        self.robots = robots
        self.logger = logging.Logger(__name__)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        self.logger.info("Stop event set.")

class TeleoperationBaseTask(BaseTask, ABC):
    def __init__(self, robots: List[RobotInterface]) -> None:
        """Base class for tasks controlling robots in a Polymetis environment

            There are two ways to specify the task: 
            1. by passing a callable object to the constructor
            2. by overriding the run() method in a subclass.

        Args:
            robots (List[RobotInterface]): robots that can be controlled by the task
        """
        super().__init__(robots)
        if len(self.robots) < 2:
            self.logger.error("Not enough robots supplied as parameter. Teleoperation requires at least two robots.")
            exit(1)
        
    def sync_robot_positions(self):
        self.logger.info(f"Moving all robots to the position of the first robot...")
        base_pos = self.robots[0].get_joint_positions()
        for robot in self.robots:
            robot.move_to_joint_positions(base_pos)
        self.logger.info(f"Robot positions synced successfully.")

class ReplayBaseTask(BaseTask, ABC):
    def __init__(self, robots: List[RobotInterface], demonstrations: List[Dict[str, torch.Tensor]]) -> None:
        super().__init__(robots)
        self.demonstrations = demonstrations
