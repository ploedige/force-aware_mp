import tkinter as tk
from omegaconf import DictConfig

from polymetis import RobotInterface

class RobotInterfaceControl(tk.Frame):
    def __init__(self, master,robot_cfg:DictConfig):
        super().__init__(master)
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

        self.status_text = tk.Text(self, wrap=tk.WORD, height=5, width=40)
        self.status_text.grid(row=2, column=0, columnspan=2, sticky="nsew")

    def start(self):
        try:
            self.robot_interface = RobotInterface(ip_address = self._robot_cfg.server_ip,
                                                 port = self._robot_cfg.robot_port)
            self._add_status("Successfully initialized interface.")
        except:
            self._add_status("Failed to initialize interface. Is the server running?")
            self.robot_interface = None

    def stop(self):
        self.robot_interface = None
        self._add_status("Robot interface connection closed.")

    def _add_status(self, status:str):
        self.status_text.insert(tk.END, status)
        self.status_text.see(tk.END)