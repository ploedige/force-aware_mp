import tkinter as tk
import subprocess, os

from omegaconf import DictConfig

class RobotControl(tk.Frame):
    def __init__(self, master:tk.Tk, robot_cfg:DictConfig):
        super().__init__(master)
        self.master = master
        self.robot_cfg = robot_cfg

        self.configure(highlightthickness=5, highlightbackground='black', padx=5, pady=5)

        self.name_label = tk.Label(self, text=self.robot_cfg.name, font=('Helvetica',14,'bold'))
        self.name_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky='ew')
        
        self.start_button = tk.Button(self, text="Start", command=self._start_robot_server)
        self.start_button.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        self.start_button.config(state=tk.NORMAL)

        self.stop_button = tk.Button(self, text="Stop", command=self._stop_robot_server)
        self.stop_button.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.stop_button.config(state=tk.DISABLED)

        self.config_button = tk.Button(self, text="Config", command=self._config_robot_server)
        self.config_button.grid(row=1, column=2, padx=5, pady=5, sticky='ew')
        self.config_button.config(state=tk.NORMAL)

        self.status_text = tk.Text(self, wrap=tk.WORD, height=10, width=50)
        self.status_text.grid(row=2, column=0, columnspan=3, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self, command=self.status_text.yview)
        self.scrollbar.grid(row=2, column=3, sticky="ns")
        self.status_text.config(yscrollcommand=self.scrollbar.set)

        self.process = None

    def _start_robot_server(self):
        command = ["launch_robot.py", 
                   "robot_client=franka_hardware",
                   f"robot_client.executable_cfg.robot_ip={self.robot_cfg.robot_ip}",
                   f"port={self.robot_cfg.robot_port}"]
        conda_env_path = subprocess.check_output(["bash", "-c", "conda info --envs | grep '*' | awk '{print $NF}'"], encoding="utf-8").strip()
        ld_lib_path = subprocess.check_output(["bash", "-c", "$LD_LIBRARY_PATH"], encoding="utf-8").strip()
        ld_lib_path = f"{ld_lib_path}:{conda_env_path}"
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = ld_lib_path
        self.process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        self.start_button.config(state=tk.DISABLED)
        self.config_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self._read_process_output()

    def _stop_robot_server(self):
        if self.process:
            self.process.terminate()
            self.process = None
        self.start_button.config(state=tk.NORMAL)
        self.config_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def _config_robot_server(self):
        raise NotImplementedError

    def _read_process_output(self):
        if self.process:
            output_line = self.process.stdout.readline()
            scroll_pos = self.status_text.yview()[1]  # Get the current position of the scroll view
            at_bottom = scroll_pos == 1.0  # Check if the scroll view is at the bottom
            self.status_text.insert(tk.END, output_line)
            if at_bottom:
                self.status_text.see(tk.END)  # Scroll to the end if it was at the bottom before
            self.after(10, self._read_process_output)