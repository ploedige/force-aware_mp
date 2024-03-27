import logging
import tkinter as tk
from tkinter import ttk
from typing import List

from polymetis import RobotInterface

from data_management.robot_data_manager import RobotDataManager
from GUI.status_log import StatusLog

class LoggingControl(tk.Frame):
    def __init__(self, master, robot_interface_controls:List[RobotInterface]):
        """Controls logging of robot data.

        Args:
            master (_type_): Parent window/frame
            robot_interface_controls (List[RobotInterface]): robots to log data from.
        """
        super().__init__(master)
        self.logger = logging.getLogger(__name__)
        self.data_managers:List[RobotDataManager] = []
        self.robot_interface_controls = robot_interface_controls
        self._init_ui()

    def _init_ui(self):
        self.configure(highlightthickness=5, highlightbackground='black', padx=5, pady=5)

        name_label = tk.Label(self, text="Logging Control", font=('Helvetica',14,'bold'))
        name_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

        # Log Information Input
        info_label = tk.Label(self, text="Logging Information", font=('Helvetica',12,'italic'))
        info_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        style = ttk.Style()
        style.configure("Padded.TEntry", padding=(5,5,5,5))
        self.log_info_input = ttk.Entry(self, width=100, font=('Helvetica',12), style="Padded.TEntry")
        self.log_info_input.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # Start Button
        self.start_button = tk.Button(self, text="Start", command=self.start)
        self.start_button.grid(row=3, column=0, padx=5, pady=5, sticky='ew')
        self.start_button.config(state=tk.NORMAL)

        # Stop Button
        self.split_button = tk.Button(self, text="Split", command=self.split)
        self.split_button.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.split_button.config(state=tk.DISABLED)

        # Config Button
        self.stop_button = tk.Button(self, text="Stop", command=self.stop)
        self.stop_button.grid(row=3, column=2, padx=5, pady=5, sticky='ew')
        self.stop_button.config(state=tk.DISABLED)

        #Status Log
        self.status_log = StatusLog(self, height=5, width=100)
        self.status_log.grid(row=4, column=0, columnspan=3, sticky="nsew")
        self.logger.addHandler(self.status_log.handler)

    def start(self):
        """start logging data from the robots."""
        robots = [ric.robot_interface for ric in self.robot_interface_controls] 
        if (robots is None or 
            len(robots) == 0 
            or any(robot is None for robot in robots)):
            self.logger.error("Robot interfaces not initialized.")
            return
        if len(self.data_managers) == 0:
            robot_cnt = 0
            for robot in robots:
                data_manager = RobotDataManager(robot, log_info=f"{self.log_info_input.get()} - Robot {robot_cnt}")
                robot_cnt += 1
                self.data_managers.append(data_manager)
                data_manager.start()
        self.start_button.config(state=tk.DISABLED)
        self.split_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.logger.info("Logging started.")

    def split(self):
        """split the incoming data at current time."""
        for data_manager in self.data_managers:
            data_manager.split()
        self.logger.info("Data split.")
        
    def stop(self):
        """stop logging data from the robots."""
        for data_manager in self.data_managers:
            data_manager.stop()
            data_manager.join()
        self.data_managers = []
        self.start_button.config(state=tk.NORMAL)
        self.split_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.logger.info("Logging stopped.")
