from controller.central_controller import CentralController
from modules.visualyzer import NetworkVisualizer3D
import tkinter as tk
import threading

def start_gui(controller):
    root = tk.Tk()
    app = NetworkVisualizer3D(root, controller)
    root.mainloop()

def main():
    controller = CentralController()
    # CLI in separatem Thread starten
    cli_thread = threading.Thread(target=controller.start_cli, daemon=True)
    cli_thread.start()
    # GUI im Hauptthread starten
    start_gui(controller)

if __name__ == "__main__":
    main()
