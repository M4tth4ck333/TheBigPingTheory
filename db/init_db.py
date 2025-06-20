from db.engine import engine
from db.models import Base

def init():
    Base.metadata.create_all(bind=engine)
    print("\u2714\ufe0f  Datenbank initialisiert")

if __name__ == "__main__":
    init()

from db.engine import engine
from db.models import Base

def init():
    Base.metadata.create_all(bind=engine)
    print("\u2714\ufe0f  Datenbank initialisiert")

if __name__ == "__main__":
    init()
