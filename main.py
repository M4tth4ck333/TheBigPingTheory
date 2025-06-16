import os
import sys
import logging
import threading
import tkinter as tk

from controller.central_controller import CentralController
from modules.visualyzer import NetworkVisualizer3D
from utils.terminal_colors import ColorSelected, colors_terminal  # Beispielpfad
from utils.hashing import calculate_hash  # Beispielpfad
from utils.sudo_check import check_sudo
from utils.hardware_check import check_hardware

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging initialized")

def start_gui(controller):
    root = tk.Tk()
    root.title("Network Visualizer 3D")
    app = NetworkVisualizer3D(root, controller)
    root.mainloop()

def start_cli(controller):
    # CLI Hook/Setup, z.B. Farben setzen und ggf. Logging in CLI-Ausgabe
    color_theme = colors_terminal["dark"]  # Beispiel: "dark"-Theme laden
    color_selected = ColorSelected(theme=color_theme)
    logging.info(f"CLI started with theme: {color_theme.primary}")

    # Hier z.B. CLI starten:
    controller.start_cli()

def main():
    setup_logging()

    # Prüfe root-Rechte oder sudo
    if not check_sudo():
        logging.error("This program requires sudo/root privileges.")
        print("Please run this program as root or with sudo.")
        sys.exit(1)

    # Prüfe Hardware
    if not check_hardware():
        logging.warning("Hardware requirements not met. Continuing with limited functionality.")

    controller = CentralController()

    # CLI in separatem Thread starten
    cli_thread = threading.Thread(target=start_cli, args=(controller,), daemon=True)
    cli_thread.start()

    # GUI im Hauptthread starten
    start_gui(controller)

if __name__ == "__main__":
    main()
