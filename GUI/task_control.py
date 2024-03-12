import tkinter as tk
from tkinter import ttk
from omegaconf import DictConfig
import inspect
import pkgutil
from typing import Dict

from polymetis import RobotInterface

import tasks
from tasks.base_tasks import BaseTask

class TaskControl(tk.Frame):
    def __init__(self, master, robots_cfg):
        super().__init__(master)
        self._tasks = self._get_tasks()
        self._init_ui(list(self._tasks.keys()))
        self._robots_cfg = robots_cfg
        self._task = None

    def _init_ui(self, task_names):
        self.configure(highlightthickness=5, highlightbackground='black', padx=5, pady=5)

        name_label = tk.Label(self, text="Task Control", font=('Helvetica',14,'bold'))
        name_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

        # Dropdown menu
        style = ttk.Style()
        style.configure("Padded.TCombobox", padding=(5,5,5,5))
        self.task_selection = ttk.Combobox(self, values=task_names, width=50, state='readonly', font=('Helvetica',12), style="Padded.TCombobox")
        self.task_selection.current(0)
        self.task_selection.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        # Start Button
        self.start_button = tk.Button(self, text="Start", command=self.start)
        self.start_button.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        self.start_button.config(state=tk.NORMAL)

        # Stop Button
        self.stop_button = tk.Button(self, text="Stop", command=self.stop)
        self.stop_button.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.stop_button.config(state=tk.DISABLED)

        # Config Button
        self.config_button = tk.Button(self, text="Config", command=self.config)
        self.config_button.grid(row=1, column=2, padx=5, pady=5, sticky='ew')
        self.config_button.config(state=tk.NORMAL)

    def start(self):
        if self._task is not None:
            return
        selected_task = self.task_selection.get()
        task_type = self._tasks[selected_task]
        self._task = task_type(self._init_robots(self._robots_cfg))
        self._task.run()
        self.start_button.config(state=tk.DISABLED)
        self.config_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)


    def stop(self):
        if self._task is not None:
            self._task.stop()
        self.start_button.config(state=tk.NORMAL)
        self.config_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def config(self):
        raise NotImplementedError

    @staticmethod
    def _init_robots(robots_cfg:DictConfig):
        robots = []
        for robot in robots_cfg:
            robots.append(RobotInterface(ip_address = robot.server_ip,
                                         port = robot.robot_port))
        return robots

    @staticmethod
    def _get_tasks()-> Dict[str, BaseTask]:
        module = tasks
        excluded_submodule = 'tasks.base_tasks'
        task_classes = dict()
        direct_submodules = set()
        for _, name, _ in pkgutil.iter_modules(module.__path__):
            submodule_name = f"{module.__name__}.{name}"
            if submodule_name == excluded_submodule:
                continue  # Skip classes from the excluded submodule
            submodule = __import__(submodule_name, fromlist=[name])
            direct_submodules.add(submodule_name)
            for _, obj in inspect.getmembers(submodule):
                if inspect.isclass(obj) and inspect.getmodule(obj).__name__ in direct_submodules:
                    task_classes[obj.__name__] = obj
        return task_classes
