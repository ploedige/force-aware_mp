import hydra

from GUI.main_window import MainWindow

@hydra.main(config_path="configs", config_name="environment")
def main(cfg):
    app = MainWindow(cfg)
    app.mainloop()

if __name__ == "__main__":
    main()