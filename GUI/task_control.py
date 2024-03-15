from omegaconf import DictConfig
from tkinter import ttk
from typing import Dict, List
import inspect
import logging
import pkgutil
import tkinter as tk

from polymetis import RobotInterface

import tasks
from tasks.base_tasks import BaseTask
from GUI.robot_interface_control import RobotInterfaceControl
from GUI.status_log import StatusLog

class TaskControl(tk.Frame):
    def __init__(self, master, robot_interface_controls: List[RobotInterfaceControl]):
        super().__init__(master)
        self.logger = logging.getLogger(__name__)
        self.robot_interface_controls = robot_interface_controls
        self._tasks = self._get_tasks()
        self._current_task = None
        self._init_ui(list(self._tasks.keys()))

    def _init_ui(self, task_names):
        self.configure(highlightthickness=5, highlightbackground='black', padx=5, pady=5)

        name_label = tk.Label(self, text="Task Control", font=('Helvetica',14,'bold'))
        name_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

        # Dropdown menu
        style = ttk.Style()
        style.configure("Padded.TCombobox", padding=(5,5,5,5))
        self.task_selection = ttk.Combobox(self, values=task_names, width=100, state='readonly', font=('Helvetica',12), style="Padded.TCombobox")
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

        #Status Log
        self.status_log = StatusLog(self, height=5, width=100)
        self.status_log.grid(row=2, column=0, columnspan=3, sticky="nsew")
        self.logger.addHandler(self.status_log.handler)

    def start(self):
        robots = [ric.robot_interface for ric in self.robot_interface_controls] 
        if (robots is None or 
            len(robots) == 0 
            or any(robot is None for robot in robots)):
            self.logger.error("Robot interfaces not initialized.")
            return
        if self._current_task is not None:
            self.logger.warning("There is already a task running. Stop it before starting a new one.")
            return
        selected_task = self.task_selection.get()
        task_type = self._tasks[selected_task]
        self._current_task = task_type(robots)
        self._current_task.start()
        self.start_button.config(state=tk.DISABLED)
        self.config_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.logger.info(f"Started task {selected_task}.")


    def stop(self):
        if self._current_task is not None:
            self._current_task.stop()
            self._current_task.join()
            self._current_task = None
        self.start_button.config(state=tk.NORMAL)
        self.config_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.logger.info("Stopped current task.")

    def config(self):
        raise NotImplementedError

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
