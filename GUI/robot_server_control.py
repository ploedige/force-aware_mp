import tkinter as tk
import subprocess, os
from queue import Queue, Empty
from threading import Thread

from omegaconf import DictConfig

from GUI.status_log import StatusLog

class RobotServerControl(tk.Frame):
    def __init__(self, master:tk.Frame, robot_cfg:DictConfig):
        """Tk module for controlling a robot server.

        Args:
            master (tk.Tk): The parent window/frame
            robot_cfg (DictConfig): Configuration of the robot 
        """
        super().__init__(master)
        self.master = master
        self.robot_cfg = robot_cfg
        self._output_read_thread = None
        self._output_queue = Queue()
        self._init_ui()
    
    def _init_ui(self):
        self.configure(highlightthickness=5, highlightbackground='black', padx=5, pady=5)

        self.name_label = tk.Label(self, text=f"Robot Server: {self.robot_cfg.name}", font=('Helvetica',14,'bold'))
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

        self.status_text = tk.Text(self, wrap=tk.WORD, height=20, width=100)
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
        ld_lib_path = subprocess.check_output(["bash", "-c", "echo $LD_LIBRARY_PATH"], encoding="utf-8").strip()
        ld_lib_path = f"{ld_lib_path}:{conda_env_path}/lib"
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

    def _enqueue_process_output(self):
        self._output_queue.put(self.process.stdout.readline())

    def _read_process_output(self):
        if self.process:
            if self._output_read_thread is None or not self._output_read_thread.is_alive():
                self._output_read_thread = Thread(target=self._enqueue_process_output)
                self._output_read_thread.daemon = True
                self._output_read_thread.start()

            try: output_line = self._output_queue.get_nowait()
            except Empty:
                pass    
            else:
                scroll_pos = self.status_text.yview()[1]  # Get the current position of the scroll view
                at_bottom = scroll_pos == 1.0  # Check if the scroll view is at the bottom
                self.status_text.insert(tk.END, output_line)
                if at_bottom:
                    self.status_text.see(tk.END)  # Scroll to the end if it was at the bottom before
            self.master.after(10, self._read_process_output)

    @staticmethod
    def stop_all_servers():
        """stops all running robot servers.
        """
        command = ["sudo", "pkill", "-9", "run_server"]
        subprocess.run(command)