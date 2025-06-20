import os
import shutil
import pathlib
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

BASE_DIR = pathlib.Path(__file__).resolve().parent
DB_PATH = os.getenv("TEAS_DB_PATH", str(BASE_DIR / "teasesraect.db"))

class DBManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{self.db_path}", connect_args={"check_same_thread": False})
        self.SessionLocal = scoped_session(sessionmaker(bind=self.engine))

    def init_db(self, base):
        """Initialisiert die DB-Struktur (alle Tabellen) anhand des gegebenen Base (declarative_base)."""
        base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        """Contextmanager für Session, sorgt für Commit/Rollback und schließt Session."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def backup_db(self, backup_dir=None):
        """Erstellt eine Sicherungskopie der SQLite-Datei."""
        backup_dir = backup_dir or (BASE_DIR / "backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = pathlib.Path(backup_dir) / f"backup_{pathlib.Path(self.db_path).stem}_{int(os.times().elapsed)}.db"
        shutil.copy2(self.db_path, backup_file)
        return backup_file

    def cleanup_sessions(self):
        """Kann genutzt werden, um Sessions oder temporäre DB-Ressourcen zu bereinigen (Platzhalter)."""
        pass

    def drop_all(self, base):
        """Löscht alle Tabellen (nur für Entwicklungszwecke)."""
        base.metadata.drop_all(self.engine)

# Beispiel, wie man es später nutzt:

# from models import Base
# dbm = DBManager()
# dbm.init_db(Base)

# with dbm.get_session() as session:
#     # DB Operationen
#     pass

# backup = dbm.backup_db()
# print(f"Backup gespeichert unter: {backup}")
