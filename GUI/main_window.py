import tkinter as tk
from tkinter import font

from GUI.robot_control import RobotControl

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        title = "FAM User Interface"
        self.title(title)

        title_label = tk.Label(self,text=title, font=("Helvetica",18,'bold'))
        title_label.grid(row=0, column=0, columnspan=2)

        demonstrator_control = RobotControl(self, "Test 1")
        demonstrator_control.grid(row=1, column=1, padx=5, pady=5)

        replicant_control = RobotControl(self, "Test 2")
        replicant_control.grid(row=2, column=1, padx=5, pady=5)
