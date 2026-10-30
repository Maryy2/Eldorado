from sqlalchemy import Column, Integer, String, Boolean, DateTime
import datetime
from database import Base

class User(Base):
    """
    Definice tabulky 'users' v databázi. 
    Každý atribut reprezentuje jeden sloupec.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)  
    is_admin = Column(Boolean, default=False)    
    tier = Column(String, default="free")        
    
    # Napojení na API Eldorada a Discord notifikace
    eldorado_client_id = Column(String, nullable=True)
    eldorado_client_secret = Column(String, nullable=True)
    discord_webhook_url = Column(String, nullable=True)
    
    # Čas vytvoření účtu (automaticky se vyplní aktuálním časem)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)