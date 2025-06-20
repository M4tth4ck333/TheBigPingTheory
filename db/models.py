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
