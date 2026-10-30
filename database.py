from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Cesta k souboru databáze. Zde se vytvoří soubor eldorado.db.
SQLALCHEMY_DATABASE_URL = "sqlite:///./eldorado.db"

# Vytvoření enginu (jádra pro komunikaci s databází). 
# check_same_thread=False je nutné pro SQLite, pokud používáme FastAPI.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Továrna na vytváření databázových relací (sessions)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Od této třídy se budou odvíjet všechny naše databázové modely v models.py
Base = declarative_base()

def get_db():
    """
    Tato funkce se stará o otevření a bezpečné zavření připojení k databázi.
    FastAPI ji bude volat pokaždé, když nějaký endpoint potřebuje pracovat s daty.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()