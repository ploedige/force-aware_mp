import tkinter as tk
from tkinter import ttk

import inspect
import pkgutil

import tasks

class TaskControl(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.configure(highlightthickness=5, highlightbackground='black', padx=5, pady=5)

        name_label = tk.Label(self, text="Task Control", font=('Helvetica',14,'bold'))
        name_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

        # Dropdown menu
        tasks = self._get_tasks()
        self.selected_task = tk.StringVar()

        style = ttk.Style()
        style.configure("Padded.TCombobox", padding=(5,5,5,5))
        self.dropdown = ttk.Combobox(self, textvariable=self.selected_task, values=tasks, width=50, state='readonly', font=('Helvetica',12), style="Padded.TCombobox")
        self.dropdown.current(0)
        self.dropdown.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        # Start Button
        self.start_button = tk.Button(self, text="Start", command=self.start)
        self.start_button.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        # Stop Button
        self.stop_button = tk.Button(self, text="Stop", command=self.stop)
        self.stop_button.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Config Button
        self.config_button = tk.Button(self, text="Config", command=self.config)
        self.config_button.grid(row=1, column=2, padx=5, pady=5, sticky='ew')

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def config(self):
        raise NotImplementedError

    @staticmethod
    def _get_tasks():
        module = tasks
        excluded_submodule = 'tasks.base_tasks'
        classes = set()
        direct_submodules = {module.__name__}
        for _, name, _ in pkgutil.iter_modules(module.__path__):
            submodule_name = f"{module.__name__}.{name}"
            if submodule_name == excluded_submodule:
                continue  # Skip classes from the excluded submodule
            submodule = __import__(submodule_name, fromlist=[name])
            direct_submodules.add(submodule_name)
            for _, obj in inspect.getmembers(submodule):
                if inspect.isclass(obj) and inspect.getmodule(obj).__name__ in direct_submodules:
                    classes.add(obj.__name__)
        return list(classes)
