import tkinter as tk
import logging

class StatusLog(tk.Frame):

    class LoggingHandler(logging.Handler):
        def __init__(self, text_widget):
            logging.Handler.__init__(self)
            self.text_widget = text_widget
        
        def emit(self, record):
            msg = self.format(record)
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, f'[{record.levelname}] {msg} \n')
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)

    def __init__(self, master, height:int=5, width:int=50, font=('Helvetica',12)):
        super().__init__(master)
        self.handler = None
        self._init_ui(height, width, font)
    
    def _init_ui(self, height:int, width:int, font):
        self.status_text = tk.Text(self, wrap=tk.WORD, height=height, width=width, font=font)
        self.status_text.config(state=tk.DISABLED)
        self.status_text.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self, command=self.status_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.config(yscrollcommand=self.scrollbar.set)

        self.handler = self.LoggingHandler(self.status_text)