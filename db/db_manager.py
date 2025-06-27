import os
import pathlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

# --- Models ---
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, JSON, Text
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Scan(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True)
    scan_type = Column(String, nullable=False)   # 'wifi', 'bluetooth', 'eth', 'wps', ...
    interface = Column(String, nullable=True)
    channel = Column(Integer, nullable=True)
    scan_time = Column(DateTime, default=datetime.utcnow)
    result_file = Column(String, nullable=True)
    result_data = Column(JSON, nullable=True)   # Parsed Scan Result als JSON

class FileHash(Base):
    __tablename__ = 'file_hashes'
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True, nullable=False)
    sha256 = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    github_url = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)

# --- DB-Setup (thread-sicher) ---
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

# --- DB-Manager ---
class DBManager:
    def __init__(self):
        Base.metadata.create_all(engine)

    def add_scan(self, **kwargs):
        session = get_session()
        try:
            scan = Scan(**kwargs)
            session.add(scan)
            session.commit()
            return scan.id
        except SQLAlchemyError as e:
            session.rollback()
            print("Fehler beim Hinzufügen des Scans:", e)
        finally:
            session.close()

    def add_file_hash(self, filename, sha256):
        session = get_session()
        try:
            file_hash = FileHash(filename=filename, sha256=sha256)
            session.add(file_hash)
            session.commit()
            return file_hash.id
        except SQLAlchemyError as e:
            session.rollback()
            print("Fehler beim Hinzufügen des FileHash:", e)
        finally:
            session.close()

    def add_module(self, name, description=None, github_url=None, enabled=True):
        session = get_session()
        try:
            module = Module(name=name, description=description, github_url=github_url, enabled=enabled)
            session.add(module)
            session.commit()
            return module.id
        except SQLAlchemyError as e:
            session.rollback()
            print("Fehler beim Hinzufügen des Moduls:", e)
        finally:
            session.close()

    def get_latest_scans(self, limit=10):
        session = get_session()
        try:
            return session.query(Scan).order_by(Scan.scan_time.desc()).limit(limit).all()
        finally:
            session.close()

    def get_enabled_modules(self):
        session = get_session()
        try:
            return session.query(Module).filter_by(enabled=True).all()
        finally:
            session.close()

# --- Beispielnutzung ---
if __name__ == "__main__":
    dbm = DBManager()
    # Beispiel: Scan hinzufügen
    scan_id = dbm.add_scan(scan_type="wifi", interface="wlan0", channel=6, result_file="scan1.json", result_data={"networks": []})
    print("Neuer Scan:", scan_id)
    # Beispiel: FileHash hinzufügen
    hash_id = dbm.add_file_hash(filename="scan1.json", sha256="abc123...")
    print("Neuer FileHash:", hash_id)
    # Beispiel: Modul hinzufügen
    mod_id = dbm.add_module(name="wifi_scanner", description="Scannt WLAN-Netze", github_url="https://github.com/example/wifi_scanner")
    print("Neues Modul:", mod_id)
    # Letzte Scans anzeigen
    for scan in dbm.get_latest_scans():
        print(scan.id, scan.scan_type, scan.interface, scan.scan_time)
    # Aktivierte Module anzeigen
    for mod in dbm.get_enabled_modules():
        print(mod.id, mod.name, mod.enabled)
