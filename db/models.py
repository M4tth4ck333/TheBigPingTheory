from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import hashlib

Base = declarative_base()

class Host(Base):
    __tablename__ = 'hosts'
    id = Column(Integer, primary_key=True)
    ip = Column(String, unique=True)
    mac = Column(String)
    os = Column(String)
    seen = Column(DateTime, default=datetime.utcnow)

class ScanModule(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    enabled = Column(Boolean, default=True)

class LogEntry(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    module = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message = Column(String)
    level = Column(String, default="INFO")

class FileHash(Base):
    __tablename__ = 'hashes'
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True)
    sha256 = Column(String)
    created = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def calculate_sha256(filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

