import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db import Base, engine
from config import validate_required_env

from routers.products import router as products_router
from routers.orders import router as orders_router
from routers.admin import router as admin_router
from routers.auth import router as auth_router
from routers.telegram import router as telegram_router

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

validate_required_env()

app = FastAPI()

raw_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,https://legolandstore.ru,https://www.legolandstore.ru,https://web.telegram.org"
)
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

# Telegram Mini App and preview domains should pass CORS preflight as well.
allowed_origin_regex = os.getenv(
    "CORS_ORIGIN_REGEX",
    r"https://([a-zA-Z0-9-]+\.)*(telegram\.org|t\.me|vercel\.app)$",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("images"):
    os.makedirs("images")
app.mount("/images", StaticFiles(directory="images"), name="images")

app.include_router(products_router)
app.include_router(orders_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(telegram_router)


@app.get("/")
def root():
    return {"status": "ok"}
