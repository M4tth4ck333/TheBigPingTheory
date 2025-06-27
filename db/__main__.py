import os
import pathlib
import threading
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, LargeBinary, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship

# --- Datenbank-Setup ---
BASE_DIR = pathlib.Path(__file__).resolve().parent
DB_PATH = os.getenv("TEAS_DB_PATH", str(BASE_DIR / "teasesraect.db"))

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)
SessionLocal = scoped_session(sessionmaker(bind=engine))

def get_session():
    """Gibt eine neue, thread-lokale Session zurück."""
    return SessionLocal()

Base = declarative_base()

# --- Datenbankmodelle ---
class FileModel(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    filetype = Column(String)
    data = Column(LargeBinary)
    timestamp = Column(String, default=lambda: datetime.datetime.now().isoformat())

class ScanModel(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True)
    scan_type = Column(String)
    result_id = Column(Integer, ForeignKey("files.id"))
    heuristik = Column(String)
    timestamp = Column(String, default=lambda: datetime.datetime.now().isoformat())
    file = relationship("FileModel")

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

# --- Datenbank-Manager ---
class DBManager:
    def add_file(self, filename, data, filetype=None):
        session = get_session()
        try:
            file_entry = FileModel(filename=filename, data=data, filetype=filetype)
            session.add(file_entry)
            session.commit()
            return file_entry.id
        finally:
            session.close()

    def add_scan(self, scan_type, file_id, heuristik):
        session = get_session()
        try:
            scan_entry = ScanModel(scan_type=scan_type, result_id=file_id, heuristik=heuristik)
            session.add(scan_entry)
            session.commit()
            return scan_entry.id
        finally:
            session.close()

    def get_latest_scans(self, limit=10):
        session = get_session()
        try:
            scans = session.query(ScanModel).order_by(ScanModel.timestamp.desc()).limit(limit).all()
            return scans
        finally:
            session.close()

    def add_qemu_vm(self, name, image_path, memory, cpus, net_mode, extra_args, status="gestoppt"):
        session = get_session()
        try:
            vm_entry = QemuVMModel(
                name=name,
                image_path=image_path,
                memory=memory,
                cpus=cpus,
                net_mode=net_mode,
                extra_args=extra_args,
                status=status
            )
            session.add(vm_entry)
            session.commit()
            return vm_entry.id
        finally:
            session.close()

    def update_qemu_vm_status(self, vm_id, status):
        session = get_session()
        try:
            vm = session.query(QemuVMModel).filter_by(id=vm_id).first()
            if vm:
                vm.status = status
                session.commit()
        finally:
            session.close()

    def get_all_qemu_vms(self):
        session = get_session()
        try:
            vms = session.query(QemuVMModel).all()
            return vms
        finally:
            session.close()

    def threaded_file_upload(self, filename, data, filetype=None):
        def worker():
            file_id = self.add_file(filename, data, filetype)
            print(f"[Thread-{threading.current_thread().name}] Datei {filename} gespeichert (ID: {file_id})")
        t = threading.Thread(target=worker)
        t.start()
        return t

# --- Beispielnutzung ---
if __name__ == "__main__":
    dbm = DBManager()
    # Beispiel: Datei speichern (multithreaded)
    threads = []
    for i in range(3):
        fname = f"testfile_{i}.txt"
        data = f"Testinhalt {i}".encode()
        t = dbm.threaded_file_upload(fname, data, filetype="text/plain")
        threads.append(t)
    for t in threads:
        t.join()
    # Beispiel: QEMU-VM speichern
    vm_id = dbm.add_qemu_vm(
        name="testbot",
        image_path="/pfad/zu/image.qcow2",
        memory=256,
        cpus=1,
        net_mode="user",
        extra_args="",
        status="gestoppt"
    )
    print("Alle VMs:", dbm.get_all_qemu_vms())
