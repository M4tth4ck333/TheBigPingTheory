import threading
import datetime
import os
import pathlib
from sqlalchemy import (create_engine, Column, Integer, String, DateTime, Boolean, JSON, Text, LargeBinary, ForeignKey)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship
import tkinter as tk

# --- Datenbank-Setup ---
BASE_DIR = pathlib.Path(__file__).resolve().parent
DB_PATH = os.getenv("DURGA_DB_PATH", str(BASE_DIR / "durga.db"))
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(bind=engine))
def get_session():
    return SessionLocal()
Base = declarative_base()

# --- Datenbankmodelle ---
class Scan(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True)
    scan_type = Column(String, nullable=False)
    interface = Column(String, nullable=True)
    channel = Column(Integer, nullable=True)
    scan_time = Column(DateTime, default=datetime.datetime.utcnow)
    result_file = Column(String, nullable=True)
    result_data = Column(JSON, nullable=True)

class FileHash(Base):
    __tablename__ = 'file_hashes'
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True, nullable=False)
    sha256 = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    github_url = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)

class QemuVMModel(Base):
    __tablename__ = "qemu_vms"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    image_path = Column(String)
    memory = Column(Integer)
    cpus = Column(Integer)
    net_mode = Column(String)
    extra_args = Column(String)
    status = Column(String)
    timestamp = Column(String, default=lambda: datetime.datetime.now().isoformat())

Base.metadata.create_all(engine)

# --- Netzwerkgeräte-Klassen mit Symbolen ---
DEVICE_SYMBOLS = {
    "Router": "🛣️",
    "Switch": "⬜↔⬜",
    "Hub": "⭕",
    "Bridge": "⎔",
    "Gateway": "🚪",
    "AccessPoint": "📡",
    "Repeater": "🔁",
    "Modem": "🌐",
    "Firewall": "🧱",
    "LoadBalancer": "⚖️"
}
DEVICE_COLORS = {
    "Router": "#FF0000",
    "Switch": "#0074D9",
    "Hub": "#AAAAAA",
    "Bridge": "#39CCCC",
    "Gateway": "#B10DC9",
    "AccessPoint": "#2ECC40",
    "Repeater": "#FF851B",
    "Modem": "#FFDC00",
    "Firewall": "#85144b",
    "LoadBalancer": "#F012BE"
}
class Device:
    def __init__(self, name, device_type):
        self.name = name
        self.device_type = device_type
        self.color = DEVICE_COLORS.get(device_type, "#CCCCCC")
        self.symbol = DEVICE_SYMBOLS.get(device_type, "❓")
    def act(self, *args, **kwargs):
        print(f"{self.device_type} {self.name}: Keine spezifische Aktion definiert (riot!)")

# --- QEMU-Basisklasse ---
import subprocess
class QemuVM:
    def __init__(self, name, image_path, memory=512, cpus=1, net_mode="user", extra_args=None):
        self.name = name
        self.image_path = image_path
        self.memory = memory
        self.cpus = cpus
        self.net_mode = net_mode
        self.extra_args = extra_args or []
        self.process = None
    def start(self):
        qemu_cmd = [
            "qemu-system-x86_64",
            "-name", self.name,
            "-m", str(self.memory),
            "-smp", str(self.cpus),
            "-hda", self.image_path,
            "-net", f"nic,model=virtio",
            "-net", f"{self.net_mode}"
        ] + self.extra_args
        print(f"[QEMU] Starte VM {self.name} ...")
        self.process = subprocess.Popen(qemu_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        threading.Thread(target=self._log_output, daemon=True).start()
    def _log_output(self):
        if self.process.stdout:
            for line in iter(self.process.stdout.readline, b''):
                print(f"[{self.name}-QEMU] {line.decode().strip()}")
    def stop(self):
        if self.process and self.process.poll() is None:
            print(f"[QEMU] Stoppe VM {self.name} ...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print(f"[QEMU] VM {self.name} gestoppt.")
    def is_running(self):
        return self.process and self.process.poll() is None
    def __del__(self):
        self.stop()

# --- DURGA Engine ---
class DurgaEngine:
    def __init__(self):
        self.db = DBManager()
        self.devices = []
        self.qemu_vms = []
        self.plugins = []
        self.arme = {}
    def add_device(self, device):
        self.devices.append(device)
    def add_qemu_vm(self, vm):
        self.qemu_vms.append(vm)
    def register_arm(self, name, handler):
        self.arme[name] = handler
    def start_all_vms(self):
        for vm in self.qemu_vms:
            vm.start()
    def stop_all_vms(self):
        for vm in self.qemu_vms:
            vm.stop()
    def run_plugin(self, name, *args, **kwargs):
        for plugin in self.plugins:
            if getattr(plugin, "name", None) == name:
                plugin.run(*args, **kwargs)
    def visualize(self):
        # Beispiel für GUI-Visualisierung (Drag-and-Drop mit Canvas)
        root = tk.Tk()
        root.title("DURGA Netzwerk-Visualisierung")
        canvas = tk.Canvas(root, width=800, height=500, bg="white")
        canvas.pack()
        for i, device in enumerate(self.devices):
            x, y = 100 + i*100, 100
            canvas.create_text(x, y, text=device.symbol, font=("Arial", 32), fill=device.color, tags=("device", device.device_type, device.name))
        root.mainloop()

# --- Datenbank-Manager ---
class DBManager:
    def add_scan(self, **kwargs):
        session = get_session()
        try:
            scan = Scan(**kwargs)
            session.add(scan)
            session.commit()
            return scan.id
        finally:
            session.close()
    def add_file_hash(self, filename, sha256):
        session = get_session()
        try:
            file_hash = FileHash(filename=filename, sha256=sha256)
            session.add(file_hash)
            session.commit()
            return file_hash.id
        finally:
            session.close()
    def add_module(self, name, description=None, github_url=None, enabled=True):
        session = get_session()
        try:
            module = Module(name=name, description=description, github_url=github_url, enabled=enabled)
            session.add(module)
            session.commit()
            return module.id
        finally:
            session.close()
    def add_qemu_vm(self, **kwargs):
        session = get_session()
        try:
            vm = QemuVMModel(**kwargs)
            session.add(vm)
            session.commit()
            return vm.id
        finally:
            session.close()
    def get_latest_scans(self, limit=10):
        session = get_session()
        try:
            return session.query(Scan).order_by(Scan.scan_time.desc()).limit(limit).all()
        finally:
            session.close()
    def get_all_qemu_vms(self):
        session = get_session()
        try:
            return session.query(QemuVMModel).all()
        finally:
            session.close()

# --- Beispielnutzung ---
if __name__ == "__main__":
    durga = DurgaEngine()
    # Geräte hinzufügen
    durga.add_device(Device("R1", "Router"))
    durga.add_device(Device("S1", "Switch"))
    durga.add_device(Device("FW1", "Firewall"))
    # QEMU-VM hinzufügen (nur als Beispiel, Image-Pfad anpassen!)
    # durga.add_qemu_vm(QemuVM("bot1", "/pfad/zu/image.qcow2"))
    # Visualisierung starten
    durga.visualize()
