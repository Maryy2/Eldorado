import time
from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
import httpx
from models import User

router = APIRouter(prefix="/api/store", tags=["Správa Obchodu"])

BASE_URL = "https://www.eldorado.gg"

# Slovník pro ukládání tokenů v paměti: { "client_id": {"token": "...", "expires_at": timestamp} }
TOKEN_CACHE = {}


async def get_eldorado_token(client_id: str, client_secret: str) -> str:
    """Načte token z paměti. Pokud vypršel nebo neexistuje, vyžádá nový z Eldorada."""
    current_time = time.time()

    # 1. Použití platného tokenu z paměti (pokud do jeho vypršení zbývá čas)
    if client_id in TOKEN_CACHE:
        cache_entry = TOKEN_CACHE[client_id]
        if current_time < cache_entry["expires_at"]:
            return cache_entry["token"]

    # 2. Vyžádání nového tokenu z Eldorada, pokud v paměti není nebo vypršel
    auth_url = f"{BASE_URL}/api/authentication/seller/token"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            auth_url,
            json={"clientId": client_id, "clientSecret": client_secret},
            headers=headers,
        )

        if resp.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Eldorado API rate limit! Počkej cca 5 minut, než vyprší limit požadavků na straně Eldorada.",
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Chyba autorizace Eldorado: {resp.text}",
            )

        data = resp.json()
        token = data.get("accessToken")

        # Token má platnost 900s (15 min). Uložíme si ho s rezervou na 800s.
        TOKEN_CACHE[client_id] = {
            "token": token,
            "expires_at": current_time + 800,
        }

        return token


@router.post("/switch-offline")
async def switch_offline(current_user: User = Depends(get_current_user)):
    """Přepne nabídky prodejce na Eldorado.gg do režimu Offline."""

    if (
        not current_user.eldorado_client_id
        or not current_user.eldorado_client_secret
    ):
        raise HTTPException(
            status_code=400,
            detail="Chybí vložené Eldorado API klíče v Nastavení.",
        )

    # Načte token (buď z paměti, nebo z API)
    token = await get_eldorado_token(
        current_user.eldorado_client_id, current_user.eldorado_client_secret
    )

    target_url = f"{BASE_URL}/api/offerUser/me/switchOffline"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(target_url, headers=headers)

            # Pokud Eldorado vyžaduje PUT místo POST
            if resp.status_code == 405:
                resp = await client.put(target_url, headers=headers)

            if resp.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Eldorado limit požadavků překročen. Zkuste to za chvíli.",
                )

            if resp.status_code not in [200, 204]:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Eldorado API chyba ({resp.status_code}): {resp.text}",
                )

            return {
                "status": "success",
                "message": "Obchod byl úspěšně přepnut do režimu Offline!",
            }

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Chyba komunikace s Eldoradem: {str(e)}",
            )