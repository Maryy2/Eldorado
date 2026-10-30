from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User

# Definuje endpoint, kam si má aplikace dojít pro přihlašovací token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI spustí tuto funkci před každým chráněným endpointem.
    Zkontroluje, jestli uživatel s poslaným emailem (tokenem) existuje v databázi.
    """
    user = db.query(User).filter(User.email == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Neplatné přihlášení")
    return user