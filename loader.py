import importlib
import os
import sys
import json
import datetime
from types import ModuleType
from typing import Dict, Optional, List

# ---------------- HTML LOGGER ----------------
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
        self.entries = []
        self._start_log()

    def _start_log(self):
        if not os.path.exists(self.logfile):
            with open(self.logfile, 'w') as f:
                f.write("<html><head><title>Module Log</title></head><body>\n")
                f.write("<style>body { font-family: monospace; }</style>\n")
                f.write(f"<h3>Log Start: {datetime.datetime.now()}</h3>\n")

    def _write(self, level, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color = self.COLOR_MAP.get(level.upper(), "#ffffff")
        entry = {"timestamp": timestamp, "level": level.upper(), "message": message}
        self.entries.append(entry)
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

    def export_json(self):
        return json.dumps(self.entries, indent=2)

# ---------------- MODULE DESCRIPTOR ----------------
class ModuleDescriptor:
    def __init__(self, name, path, category="default", description="", version="?", author="?"):
        self.name = name
        self.path = path
        self.category = category
        self.description = description
        self.version = version
        self.author = author

# ---------------- MODULE REGISTRY ----------------
class ModuleRegistry:
    def __init__(self):
        self.modules: Dict[str, ModuleDescriptor] = {}

    def register(self, name: str, path: str, category: str = "default", description: str = "", version: str = "?", author: str = "?"):
        self.modules[name] = ModuleDescriptor(name, path, category, description, version, author)

    def auto_register_folder(self, folder: str, base_package: str = ""):
        for filename in os.listdir(folder):
            if filename.endswith(".py") and not filename.startswith("_"):
                name = filename[:-3]
                mod_path = f"{base_package}.{name}" if base_package else name
                try:
                    mod = importlib.import_module(mod_path)
                    version = getattr(mod, "__version__", "?")
                    author = getattr(mod, "__author__", "?")
                    desc = getattr(mod, "__description__", "(Kein Beschreibungstext)")
                    self.register(name=name, path=mod_path, category="auto", description=desc, version=version, author=author)
                except Exception as e:
                    print(f"[Fehler] Kann Modul {name} nicht analysieren: {e}")

# ---------------- MODULE LOADER ----------------
class ModuleLoader:
    def __init__(self, registry: ModuleRegistry, logger: Optional[HTMLLogger] = None):
        self.registry = registry
        self.loaded: Dict[str, Optional[ModuleType]] = {}
        self.logger = logger or HTMLLogger()

    def load_all(self):
        for name, desc in self.registry.modules.items():
            try:
                mod = importlib.import_module(desc.path)
                self.loaded[name] = mod
                self.logger.module(
                    f"✅ <b>{name}</b> v{desc.version} by {desc.author} – <i>{desc.description}</i>"
                )
            except ImportError as e:
                self.loaded[name] = None
                self.logger.error(f"❌ Fehler beim Laden von <b>{name}</b>: {e}")
        return self.loaded
