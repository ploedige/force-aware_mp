import tkinter as tk
import subprocess

# from polymetis import RobotInterface

class RobotControl(tk.Frame):
    def __init__(self, master:tk.Tk, robot_name:str):#, robot: RobotInterface):
        super().__init__(master)
        self.master = master

        self.name_label = tk.Label(self, text=robot_name)
        self.name_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky='ew')
        
        self.start_button = tk.Button(self, text="Start", command=self._start_robot_server)
        self.start_button.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.stop_button = tk.Button(self, text="Stop", command=self._stop_robot_server)
        self.stop_button.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        self.config_button = tk.Button(self, text="Config", command=self._config_robot_server)
        self.config_button.grid(row=1, column=2, padx=5, pady=5, sticky='ew')

        self.status_text = tk.Text(self, wrap=tk.WORD, height=20, width=50)
        self.status_text.grid(row=2, column=0, columnspan=3, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self, command=self.status_text.yview)
        self.scrollbar.grid(row=2, column=3, sticky="ns")
        self.status_text.config(yscrollcommand=self.scrollbar.set)

        self.process = None

    def _start_robot_server(self):
        raise NotImplementedError

    def _stop_robot_server(self):
        raise NotImplementedError

    def _config_robot_server(self):
        raise NotImplementedError

    def _read_process_output(self):
        if self.process:
            output_line = self.process = self.process.stdout.readline()
            self.status_text.insert(tk.END, output_line)
            self.status_text.see(tk.END)
            self.master.after(100, self._read_process_output)