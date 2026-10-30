import bcrypt
import httpx

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Ověří, zda zadané heslo odpovídá zahošovanému heslu v databázi."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8')[:72], hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Zahashuje heslo před jeho uložením do databáze."""
    return bcrypt.hashpw(password.encode('utf-8')[:72], bcrypt.gensalt()).decode('utf-8')

async def send_discord_notification(webhook_url: str, order_id: str, buyer: str, amount: float, status: str):
    """Asynchronně odešle zprávu o objednávce na Discord kanál."""
    if not webhook_url:
        return

    # Barva rámečku na Discordu: Zelená pro 'Completed', žlutá pro ostatní
    color = 0x28a745 if status.lower() == "completed" else 0xffc107
    
    payload = {
        "username": "Eldorado Dashboard",
        "embeds": [{
            "title": f"🛒 Aktualizace objednávky: {order_id}",
            "color": color,
            "fields": [
                {"name": "Kupující", "value": buyer, "inline": True},
                {"name": "Částka", "value": f"${amount}", "inline": True},
                {"name": "Stav", "value": status, "inline": True}
            ]
        }]
    }

    # Použití httpx pro moderní asynchronní HTTP požadavky bez blokování serveru
    async with httpx.AsyncClient() as client:
        try:
            await client.post(webhook_url, json=payload)
        except Exception as e:
            print(f"Chyba při odesílání na Discord: {e}")