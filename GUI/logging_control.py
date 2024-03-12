import tkinter as tk
from tkinter import ttk

class LoggingControl(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

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

        # Stop Button
        self.split_button = tk.Button(self, text="Split", command=self.split)
        self.split_button.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        # Config Button
        self.stop_button = tk.Button(self, text="Stop", command=self.stop)
        self.stop_button.grid(row=3, column=2, padx=5, pady=5, sticky='ew')

    def start(self):
        raise NotImplementedError

    def split(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError