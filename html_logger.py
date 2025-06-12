import datetime

class HTMLLogger:
    def __init__(self, filename="report.html"):
        self.filename = filename
        with open(self.filename, "w") as f:
            f.write("<html><head><title>Passwort-Profiling Report</title></head><body>")
            f.write(f"<h1>Report vom {datetime.datetime.now()}</h1>")

    def log_section(self, title, content):
        with open(self.filename, "a") as f:
            f.write(f"<h2>{title}</h2>")
            f.write(f"<pre>{content}</pre>")

    def close(self):
        with open(self.filename, "a") as f:
            f.write("</body></html>")
