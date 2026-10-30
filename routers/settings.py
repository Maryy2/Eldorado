from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import SettingsUpdate
from dependencies import get_current_user
from utils import send_discord_notification

router = APIRouter(tags=["Nastavení"])

@router.get("/api/settings")
async def get_settings(current_user: User = Depends(get_current_user)):
    """Vrátí aktuální nastavení uživateli na frontend (bez tajného klíče)."""
    return {
        "username": current_user.username,
        "client_id": current_user.eldorado_client_id,
        "has_secret": bool(current_user.eldorado_client_secret),
        "discord_webhook_url": current_user.discord_webhook_url
    }

@router.post("/api/settings")
async def update_settings(settings: SettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Přepíše nastavení uživatele v databázi, pokud byla poslána nová data."""
    if settings.username is not None:
        current_user.username = settings.username
    if settings.client_id is not None:
        current_user.eldorado_client_id = settings.client_id
    if settings.client_secret:
        current_user.eldorado_client_secret = settings.client_secret
    if settings.discord_webhook_url is not None:
        current_user.discord_webhook_url = settings.discord_webhook_url

    db.commit()
    return {"message": "Settings updated"}

@router.post("/api/test-discord")
async def test_discord_webhook(background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """Vyzkouší odeslat testovací notifikaci do Discordu na pozadí (neblokuje API)."""
    if not current_user.discord_webhook_url:
        raise HTTPException(status_code=400, detail="Nemáš nastavenou Discord Webhook URL v nastavení!")

    # Přidá úkol do fronty, odešle se bez zdržování odpovědi frontendu
    background_tasks.add_task(
        send_discord_notification,
        webhook_url=current_user.discord_webhook_url,
        order_id="TEST-12345",
        buyer="Testovací Kupující",
        amount=10.00,
        status="Completed"
    )
    return {"message": "Odesláno na Discord"}
