# --- Imports ---
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import readline  # Für CLI Autovervollständigung

from load_plugins import load_plugins
from html_logger import HTMLLogger

# --- Beispiel-Daten ---
passwords = ["pass123", "welcome", "admin2024", "qwerty"]
usernames = ["alice", "bob"]
wlan_list = [
    {'ssid': 'WLAN-1', 'bssid': '00:11:22:33:44:55'},
    {'ssid': 'WLAN-2', 'bssid': '66:77:88:99:AA:BB'}
]

# --- Zentrales Controller-Modul ---
class CentralController:
    def __init__(self):
        self.plugins = load_plugins()
        self.data = {}
        self.passwords = passwords
        self.usernames = usernames
        self.wlan_list = wlan_list
        self.lock = threading.Lock()

    def run_plugins(self):
        results = []
        with self.lock:
            for plugin in self.plugins:
                pname = plugin.__class__.__name__
                if pname == "SocialAnalyzerPlugin":
                    for username in self.usernames:
                        result = plugin.run(username)
                        results.append((f"SocialAnalyzer: {username}", result))
                elif pname == "CreepyContext":
                    result = plugin.run(self.wlan_list)
                    results.append(("Creepy WLAN Mapping", result))
                else:
                    result = plugin.run(self.passwords)
                    results.append((pname, result))
        return results

    def scan_networks(self):
        # Dummy-Implementierung, später durch Scapy ersetzen
        with self.lock:
            return ["Network1", "Network2", "Network3"]

    def html_report(self, filename="profiling_report.html"):
        logger = HTMLLogger(filename)
        with self.lock:
            for plugin in self.plugins:
                pname = plugin.__class__.__name__
                if pname == "SocialAnalyzerPlugin":
                    for username in self.usernames:
                        result = plugin.run(username)
                        logger.log_section(f"SocialAnalyzer: {username}", str(result))
                elif pname == "CreepyContext":
                    result = plugin.run(self.wlan_list)
                    logger.log_section("Creepy WLAN Mapping", str(result))
                else:
                    result = plugin.run(self.passwords)
                    logger.log_section(pname, str(result))
        logger.close()
        print(f"HTML-Report wurde erstellt: {filename}")

# --- Tkinter GUI ---
class AppGUI(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Security Toolkit GUI")
        self.geometry("500x350")
        self.create_widgets()

    def create_widgets(self):
        self.scan_btn = ttk.Button(self, text="Scan Networks", command=self.scan_networks)
        self.scan_btn.pack(pady=5)
        self.plugin_btn = ttk.Button(self, text="Run Plugins", command=self.run_plugins)
        self.plugin_btn.pack(pady=5)
        self.report_btn = ttk.Button(self, text="Create HTML Report", command=self.create_report)
        self.report_btn.pack(pady=5)
        self.output = tk.Text(self, height=12)
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def scan_networks(self):
        networks = self.controller.scan_networks()
        self.output.insert(tk.END, f"Networks found: {networks}\n")

    def run_plugins(self):
        results = self.controller.run_plugins()
        for section, res in results:
            self.output.insert(tk.END, f"{section}: {res}\n")

    def create_report(self):
        self.controller.html_report()
        messagebox.showinfo("Report", "HTML-Report wurde erstellt.")

# --- CLI mit Autovervollständigung ---
def cli_autocomplete(text, state):
    commands = ['scan', 'plugins', 'report', 'exit', 'help']
    options = [cmd for cmd in commands if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

def start_cli(controller):
    readline.parse_and_bind("tab: complete")
    readline.set_completer(cli_autocomplete)
    print("Welcome to the Security Toolkit CLI. Type 'help' for commands.")
    while True:
        try:
            cmd = input(">>> ").strip()
            if cmd == "exit":
                print("Exiting CLI.")
                break
            elif cmd == "help":
                print("Commands: scan, plugins, report, exit")
            elif cmd == "scan":
                nets = controller.scan_networks()
                print("Networks found:", nets)
            elif cmd == "plugins":
                results = controller.run_plugins()
                for section, res in results:
                    print(f"{section}: {res}")
            elif cmd == "report":
                controller.html_report()
            else:
                print("Unknown command. Type 'help' for commands.")
        except KeyboardInterrupt:
            print("\nExiting CLI.")
            break

# --- Hauptprogramm ---
if __name__ == "__main__":
    controller = CentralController()

    # CLI in separatem Thread starten
    cli_thread = threading.Thread(target=start_cli, args=(controller,), daemon=True)
    cli_thread.start()

    # GUI im Hauptthread starten
    app = AppGUI(controller)
    app.mainloop()
