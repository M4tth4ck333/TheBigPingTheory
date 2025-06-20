from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pathlib
import os

from models import Base

BASE_DIR = pathlib.Path(__file__).resolve().parent
DB_FILE = os.getenv("TEAS_DB_PATH", str(BASE_DIR / "teasesraect.db"))

engine = create_engine(f"sqlite:///{DB_FILE}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)

def init_db():
    print(f"Erstelle DB und Tabellen in: {DB_FILE}")
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
