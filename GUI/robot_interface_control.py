import logging
import tkinter as tk
from omegaconf import DictConfig

from polymetis import RobotInterface

from GUI.status_log import StatusLog

class RobotInterfaceControl(tk.Frame):
    def __init__(self, master: tk.Frame,robot_cfg:DictConfig):
        """Tk module for controlling a robot API.

        Args:
            master (tk.Frame): Parent window/frame
            robot_cfg (DictConfig): configuration of the robot
        """
        super().__init__(master)
        self.logger = logging.getLogger(f"{__name__}({robot_cfg.name})")
        self._robot_cfg = robot_cfg
        self.robot_interface = None
        self._init_ui()

    def _init_ui(self):
        self.configure(highlightthickness=5, highlightbackground='black', padx=5, pady=5)

        name_label = tk.Label(self, text=f"Robot Interface: {self._robot_cfg.name}", font=('Helvetica',14,'bold'))
        name_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        # Start Button
        self.start_button = tk.Button(self, text="Start", command=self.start)
        self.start_button.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        self.start_button.config(state=tk.NORMAL)

        # Stop Button
        self.stop_button = tk.Button(self, text="Stop", command=self.stop)
        self.stop_button.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.stop_button.config(state=tk.DISABLED)

        self.status_log = StatusLog(self, height=5, width=50)
        self.status_log.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.logger.addHandler(self.status_log.handler)

    def start(self):
        try:
            self.robot_interface = RobotInterface(ip_address = self._robot_cfg.server_ip,
                                                 port = self._robot_cfg.robot_port)
            self.logger.info("Successfully initialized interface.")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        except:
            self.logger.error("Failed to initialize interface. Is the server running?")
            self.robot_interface = None

    def stop(self):
        self.robot_interface = None
        self.logger.info("Robot interface connection closed.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)