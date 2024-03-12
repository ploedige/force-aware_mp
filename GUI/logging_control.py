import tkinter as tk
from tkinter import ttk
from typing import List

from polymetis import RobotInterface

from data_magement.robot_data_manager import RobotDataManager

class LoggingControl(tk.Frame):
    def __init__(self, master, robots:List[RobotInterface]):
        super().__init__(master)
        self.data_managers:List[RobotDataManager] = []
        self.robots = robots
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
        self.log_info_input = ttk.Entry(self, width=50, font=('Helvetica',12), style="Padded.TEntry")
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

    def start(self):
        if len(self.data_managers) == 0:
            for robot in self.robots:
                data_manager = RobotDataManager(robot,self.log_info_input.get())
                self.data_managers.append(data_manager)
                data_manager.start()
        self.start_button.config(state=tk.DISABLED)
        self.split_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)

    def split(self):
        for data_manager in self.data_managers:
            data_manager.split()
        
    def stop(self):
        for data_manager in self.data_managers:
            data_manager.stop()
        self.data_managers = []
        self.start_button.config(state=tk.NORMAL)
        self.split_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)