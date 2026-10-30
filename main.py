from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from database import engine, Base
from routers import auth, settings, orders, store

# Vytvoření tabulek v databázi z models.py, pokud soubor eldorado.db zatím neexistuje
Base.metadata.create_all(bind=engine)

# Nastavení hlavní aplikace FastAPI
app = FastAPI(
    title="Eldorado Dashboard pro Maryxz",
    description="Backend řídící obchodní data z Eldorado.gg"
)

# Inicializace složky 'templates' (kde máš uložený svůj index.html)
templates = Jinja2Templates(directory="templates")

# Připojení (inkludování) všech oddělených funkcionalit
app.include_router(auth.router)
app.include_router(settings.router)
app.include_router(orders.router)
app.include_router(store.router)

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    """Základní routa – jakmile otevřeš prohlížeč na localhost:8000, pošle ti to tvůj index.html"""
    return templates.TemplateResponse(request=request, name="index.html")