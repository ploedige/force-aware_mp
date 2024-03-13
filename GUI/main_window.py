import tkinter as tk
from tkinter import font

from omegaconf import DictConfig

from polymetis import RobotInterface

from GUI.robot_control import RobotControl
from GUI.task_control import TaskControl
from GUI.logging_control import LoggingControl

class MainWindow(tk.Tk):
    def __init__(self, env_cfg:DictConfig):
        super().__init__()
        title = "FAM User Interface"
        self.title(title)

        title_label = tk.Label(self,text=title, font=("Helvetica",18,'bold'))
        title_label.grid(row=0, column=0, columnspan=2)

        task_control = TaskControl(self,env_cfg.robots)
        task_control.grid(row=1, column=0, padx=5, pady=5)

        # log_control = LoggingControl(self)
        # log_control.grid(row=2, column=0, padx=0, pady=0)

        demonstrator_control = RobotControl(self, env_cfg.robots[0])
        demonstrator_control.grid(row=1, column=1, padx=5, pady=5)

        replicant_control = RobotControl(self, env_cfg.robots[1])
        replicant_control.grid(row=2, column=1, padx=5, pady=5)
