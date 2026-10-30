from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserRegister
from utils import get_password_hash, verify_password

# Tag 'Autentizace' se propíše do automatické dokumentace (http://localhost:8000/docs)
router = APIRouter(tags=["Autentizace"])

@router.post("/api/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Zpracuje data z registračního formuláře a vytvoří uživatele v DB."""
    
    # Kontrola, zda email už neexistuje
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Uživatel s tímto emailem již existuje.")
    
    # Vytvoření záznamu
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "Úspěšně zaregistrováno!"}

@router.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Ověří heslo a vrátí přihlašovací token (zatím posíláš e-mail jako token)."""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Nesprávný email nebo heslo")
    
    return {"access_token": user.email, "token_type": "bearer"}