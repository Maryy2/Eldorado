from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
import httpx
from pydantic import BaseModel

from models import User
from dependencies import get_current_user
from utils import send_discord_notification

router = APIRouter(tags=["Objednávky"])

BASE_URL = "https://www.eldorado.gg"

# Schema pro příchozí data z frontendu
class DiscordPayload(BaseModel):
    order_id: str
    buyer: str
    amount: float
    status: str

@router.get("/api/orders")
async def get_orders(current_user: User = Depends(get_current_user)):
    """Stáhne všechny prodejní objednávky daného uživatele z Eldorado.gg."""
    
    if not current_user.eldorado_client_id or not current_user.eldorado_client_secret:
        return {"error": "Chybí vložené Eldorado API klíče v Nastavení."}

    auth_url = f"{BASE_URL}/api/authentication/seller/token"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    async with httpx.AsyncClient() as client:
        try:
            # 1. Krok: Získání dočasného přístupového tokenu z Eldorada
            token_resp = await client.post(
                auth_url, 
                json={
                    "clientId": current_user.eldorado_client_id, 
                    "clientSecret": current_user.eldorado_client_secret
                }, 
                headers=headers
            )
            
            if token_resp.status_code != 200:
                return {"error": "Nelze získat token z Eldorada (zkontroluj Client ID / Secret)"}
            
            token = token_resp.json().get("accessToken")
            orders_headers = headers.copy()
            orders_headers["Authorization"] = f"Bearer {token}"

            all_results = []
            cursor_value = None

            # 2. Krok: Smyčka pro stažení všech stran (tzv. paginace)
            while True:
                orders_url = f"{BASE_URL}/api/v1/orders/me/seller/orders?displayFilter=DisplayBuyingOrders&pageSize=50"
                if cursor_value:
                    orders_url += f"&cursorValue={cursor_value}&pageDirection=Next"

                orders_resp = await client.get(orders_url, headers=orders_headers)
                if orders_resp.status_code != 200:
                    return {"error": f"Chyba při stahování z API: {orders_resp.text}"}

                data = orders_resp.json()
                results = data.get("results", [])
                
                if not results:
                    break

                all_results.extend(results)
                
                # Načtení kurzoru pro další stranu. Pokud není nebo je výsledků málo, smyčka končí.
                cursor_value = data.get("nextPageCursor")
                if not cursor_value or len(results) < 50:
                    break

            return {"results": all_results}

        except Exception as e:
            return {"error": f"Chyba komunikace s Eldoradem: {str(e)}"}

#test
@router.post("/api/post-discord")
async def test_discord_webhook(
    payload: DiscordPayload,
    background_tasks: BackgroundTasks
):

    # Přidání úkolu do background tasků s daty z formuláře
    background_tasks.add_task(
        send_discord_notification,
        webhook_url="https://discord.com/api/webhooks/1564968413078487211/rnj7oXOfiqLgwSTr5zkRCw6nRZOUZHI0xYQZKlT-QP2ePyipNr4voFqurtbW1SvxH3vH",
        order_id=payload.order_id,
        buyer=payload.buyer,
        amount=payload.amount,
        status=payload.status
    )
    return {"message": "Odesláno na Discord"}
