from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# --- PŘIPOJENÍ K SUPABASE (POSTGRESQL) ---
# Tady vlož URI ze Supabase (Settings -> Database -> Connection String -> URI).
# Nezapomeň v odkazu přepsat [YOUR-PASSWORD] na své skutečné heslo k databázi.
# DŮLEŽITÉ: Odkaz musí začínat "postgresql://" (nikoliv jen "postgres://").
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE")

# Vytvoření enginu (jádra pro komunikaci s PostgreSQL).
# PostgreSQL nepotřebuje connect_args={"check_same_thread": False}, to platilo jen pro SQLite.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Továrna na vytváření databázových relací (sessions)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Od této třídy se budou odvíjet všechny naše databázové modely v models.py
Base = declarative_base()

def get_db():
    """
    Tato funkce se stará o otevření a bezpečné zavření připojení k databázi na Supabase.
    FastAPI ji bude volat pokaždé, když nějaký endpoint potřebuje pracovat s daty.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()