import datetime
import os

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
        self._start_log()

    def _start_log(self):
        if not os.path.exists(self.logfile):
            with open(self.logfile, 'w') as f:
                f.write("<html><head><title>Module Log</title></head><body>\n")
                f.write("<h2>Module Log Started: {}</h2>\n".format(datetime.datetime.now()))
                f.write("<style>body { font-family: monospace; }</style>\n")

    def _write(self, level, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color = self.COLOR_MAP.get(level.upper(), "#ffffff")
        with open(self.logfile, 'a') as f:
            f.write(f'<div style="color:{color}">[{timestamp}] [{level.upper()}] {message}</div>\n')

    def info(self, msg): self._write("INFO", msg)
    def warning(self, msg): self._write("WARNING", msg)
    def error(self, msg): self._write("ERROR", msg)
    def debug(self, msg): self._write("DEBUG", msg)
    def critical(self, msg): self._write("CRITICAL", msg)
    def module(self, msg): self._write("MODULE", msg)

    def close(self):
        with open(self.logfile, 'a') as f:
            f.write("</body></html>\n")
