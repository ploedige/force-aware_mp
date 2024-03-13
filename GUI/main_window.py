import tkinter as tk
from tkinter import font

from omegaconf import DictConfig

from polymetis import RobotInterface

from GUI.robot_server_control import RobotServerControl
from GUI.robot_interface_control import RobotInterfaceControl
from GUI.task_control import TaskControl
from GUI.logging_control import LoggingControl

class MainWindow(tk.Tk):
    def __init__(self, env_cfg:DictConfig):
        super().__init__()
        title = "FAM User Interface"
        self.title(title)

        title_label = tk.Label(self,text=title, font=("Helvetica",18,'bold'))
        title_label.grid(row=0, column=0, columnspan=2)

        demonstrator_interface_control = RobotInterfaceControl(self, env_cfg.robots[0])
        demonstrator_interface_control.grid(row=1, column=0, padx=5, pady=5)

        replicant_interface_control = RobotInterfaceControl(self, env_cfg.robots[1])
        replicant_interface_control.grid(row=1, column=1, padx=5, pady=5)

        robot_interfaces = [demonstrator_interface_control.robot_interface, replicant_interface_control.robot_interface]

        task_control = TaskControl(self,robot_interfaces)
        task_control.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        log_control = LoggingControl(self, robot_interfaces)
        log_control.grid(row=3, column=0, columnspan=2, padx=0, pady=0)

        demonstrator_server = RobotServerControl(self, env_cfg.robots[0])
        demonstrator_server.grid(row=1, column=2, padx=5, pady=5)

        replicant_server = RobotServerControl(self, env_cfg.robots[1])
        replicant_server.grid(row=2, column=2, padx=5, pady=5)
