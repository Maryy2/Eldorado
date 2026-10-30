from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    """Očekávaná data z frontendu při registraci nového uživatele."""
    username: str
    email: str
    password: str

class SettingsUpdate(BaseModel):
    """Očekávaná data při ukládání nastavení. Optional znamená, že pole nemusí být vyplněno."""
    username: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    discord_webhook_url: Optional[str] = None