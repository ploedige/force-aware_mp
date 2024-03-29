import tkinter as tk
from omegaconf import DictConfig
import time

from GUI.robot_server_control import RobotServerControl
from GUI.robot_interface_control import RobotInterfaceControl
from GUI.task_control import TaskControl
from GUI.logging_control import LoggingControl

class MainWindow(tk.Tk):
    def __init__(self, env_cfg:DictConfig):
        super().__init__()
        title = "FAM User Interface"
        self.env_cfg = env_cfg
        self._init_ui(title)

    def _init_ui(self, title:str):
        self.title(title)

        title_label = tk.Label(self,text=title, font=("Helvetica",18,'bold'))
        title_label.pack(padx=5, pady=5)

        content_frame = tk.Frame(self)
        content_frame.pack()

        main_ui_frame = tk.Frame(content_frame)
        main_ui_frame.grid(row=0, column=0)

        robot_interfaces_frame = tk.Frame(main_ui_frame)
        robot_interfaces_frame.pack()

        demonstrator_interface_control = RobotInterfaceControl(robot_interfaces_frame, self.env_cfg.robots[0])
        demonstrator_interface_control.grid(row=0, column=0, padx=5, pady=5)

        replicant_interface_control = RobotInterfaceControl(robot_interfaces_frame, self.env_cfg.robots[1])
        replicant_interface_control.grid(row=0,column=1, padx=5, pady=5)

        task_control = TaskControl(main_ui_frame,[demonstrator_interface_control, replicant_interface_control])
        task_control.pack(padx=5, pady=5)

        log_control = LoggingControl(main_ui_frame, [demonstrator_interface_control, replicant_interface_control])
        log_control.pack(padx=5, pady=5)

        robot_server_frame = tk.Frame(content_frame)
        robot_server_frame.grid(row=0, column=1)

        demonstrator_server = RobotServerControl(robot_server_frame, self.env_cfg.robots[0])
        replicant_server = RobotServerControl(robot_server_frame, self.env_cfg.robots[1])

        def _start_robot_interfaces():
            replicant_interface_control.start()
            demonstrator_interface_control.start()

        def _start_robots_full():
            demonstrator_server.start()
            replicant_server.start()
            self.after(2000, _start_robot_interfaces)

        start_robot_full_button = tk.Button(robot_server_frame, text="Start All Robots (Servers & Interfaces)", command=_start_robots_full, font=("Helvetica",14, 'bold'))
        server_stop_button = tk.Button(robot_server_frame, text="Stop All Servers", command=RobotServerControl.stop_all_servers, font=("Helvetica",14, 'bold'), width=50)

        start_robot_full_button.pack(padx=5, pady=5)
        server_stop_button.pack(padx=5, pady=5)
        demonstrator_server.pack(padx=5, pady=5)
        replicant_server.pack(padx=5, pady=5)

