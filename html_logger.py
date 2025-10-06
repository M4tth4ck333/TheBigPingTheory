import datetime
import os
import threading # Neu: Für Thread-Sicherheit

class HTMLLogger:
    COLOR_MAP = {
        "INFO": "#00cc66",
        "WARNING": "#ffcc00",
        "ERROR": "#ff3333",
        "DEBUG": "#3399ff",
        "CRITICAL": "#cc0000",
        "MODULE": "#ccccff"
    }

    def __init__(self, logfile="log.html"):
        self.logfile = logfile
        self.lock = threading.Lock() # Initialisiere den Lock für Threads
        self._start_log()

    def _get_html_header(self):
        """Generiert den HTML-Header mit CSS-Klassen."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Module Log</title>
    <style>
        body {{ font-family: monospace; background-color: #1e1e1e; color: #ffffff; }}
        .log-entry {{ margin: 2px 0; padding: 0 5px; }}
        .INFO {{ color: {self.COLOR_MAP['INFO']}; }}
        .WARNING {{ color: {self.COLOR_MAP['WARNING']}; }}
        .ERROR {{ color: {self.COLOR_MAP['ERROR']}; }}
        .DEBUG {{ color: {self.COLOR_MAP['DEBUG']}; }}
        .CRITICAL {{ color: {self.COLOR_MAP['CRITICAL']}; }}
        .MODULE {{ color: {self.COLOR_MAP['MODULE']}; }}
        .timestamp {{ color: #777777; margin-right: 10px; }}
        h2 {{ color: #ffffff; border-bottom: 1px solid #333333; padding-bottom: 5px; }}
    </style>
</head>
<body>
<h2>Module Log Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h2>
"""

    def _start_log(self):
        if not os.path.exists(self.logfile):
            with open(self.logfile, 'w') as f:
                f.write(self._get_html_header())
    
    def _write(self, level, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        level_upper = level.upper()
        
        # NEU: Verwende den Lock, um nur einen Thread gleichzeitig schreiben zu lassen
        with self.lock: 
            # NEU: Verwende CSS-Klassen anstelle von Inline-Styles
            html_line = (f'<div class="log-entry {level_upper}">'
                         f'<span class="timestamp">[{timestamp}]</span>'
                         f'[{level_upper}] {message}</div>\n')
            
            with open(self.logfile, 'a') as f:
                f.write(html_line)

    # ... (Die Methoden info, warning, error, debug, critical, module bleiben gleich)
    def info(self, msg): self._write("INFO", msg)
    def warning(self, msg): self._write("WARNING", msg)
    def error(self, msg): self._write("ERROR", msg)
    def debug(self, msg): self._write("DEBUG", msg)
    def critical(self, msg): self._write("CRITICAL", msg)
    def module(self, msg): self._write("MODULE", msg)

    def close(self):
        with self.lock:
            with open(self.logfile, 'a') as f:
                f.write("</body></html>\n")

    # NEU: Kontext-Manager-Protokoll, um close() automatisch aufzurufen
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Beispiel für die Verwendung im Kontext-Manager:
# if __name__ == "__main__":
#     with HTMLLogger("test_log.html") as logger:
#         logger.info("Anwendung gestartet.")
#         logger.error("Fehler bei der Initialisierung.")
#     # Die close()-Methode wird hier automatisch aufgerufen
