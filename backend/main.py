import json
import os
import time
import uuid
import requests
import secrets
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from fastapi import Depends
from fastapi import Header, HTTPException, Request
from fastapi import UploadFile, File
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from supabase import create_client
from auth import verify_telegram_login, create_jwt, get_current_user_id
from sqlalchemy import Boolean

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

ADMIN_KEY = os.getenv("ADMIN_KEY")
FRONTEND_URL = (os.getenv("FRONTEND_URL") or "").rstrip("/")

app = FastAPI()
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)
PRODUCTS_FILE ="products.json"

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
    
def save_products(products_list):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products_list, f, ensure_ascii=False, indent=2)

def send_telegram_message(text: str):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("Telegram env not set, skip notify")
        return

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print("Telegram error:", r.status_code, r.text)
    except Exception as e:
        print("Telegram exception:", e)

def send_telegram_reply(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# CORS (обязательно для Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("images"):
    os.makedirs("images")
app.mount("/images", StaticFiles(directory="images"), name="images")

products = load_products()

class OrderItem(BaseModel):
    id: int
    title: str
    price: int
    quantity: int

class Order(BaseModel):
    name: str
    phone: str
    items: List[OrderItem]
    total: int

class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    status = Column(String)
    total = Column(Integer)
    created_at = Column(BigInteger)
    user_id = Column(BigInteger, nullable=True)

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(Integer)
    image = Column(String)

class UserModel(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)

class AuthSessionModel(Base):
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    telegram_id = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger)
    used = Column(Boolean, default=False)

class TelegramAuthPayload(BaseModel):
    data: Dict[str, Any]

Base.metadata.create_all(bind=engine)

ORDERS_FILE = "orders.json"

def check_admin_key(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

def upsert_user_and_get_id(telegram_id, username, first_name, last_name, photo_url):
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.telegram_id == telegram_id).first()

        if user:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.photo_url = photo_url
            db.commit()
            db.refresh(user)
            return user.id

        new_user = UserModel(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            photo_url=photo_url,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.id

    finally:
        db.close()

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
    
def get_user_id_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return get_current_user_id(credentials)

def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(optional_security)
):
    if not credentials:
        return None
    return get_current_user_id(credentials)

def save_orders(orders_list):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders_list, f, ensure_ascii=False, indent=2)
orders = load_orders()

def attach_telegram_to_session(code: str, telegram_id: int):
    db = SessionLocal()

    session = db.query(AuthSessionModel).filter(
        AuthSessionModel.code == code,
        AuthSessionModel.used == False
    ).first()

    if not session:
        db.close()
        return False

    session.telegram_id = telegram_id
    db.commit()
    db.close()
    return True

@app.get("/products")
def get_products():
    db = SessionLocal()
    db_products = db.query(ProductModel).all()
    db.close()

    return [
        {
            "id": p.id,
            "title": p.title,
            "price": p.price,
            "image": p.image,
        }
        for p in db_products
    ]


@app.post("/admin/products")
def add_product(product: dict, _=Depends(check_admin_key)):
    db = SessionLocal()

    new_product = ProductModel(
        title=product.get("title"),
        price=product.get("price"),
        image=product.get("image"),
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    db.close()

    return {
        "status": "ok",
        "product": {
            "id": new_product.id,
            "title": new_product.title,
            "price": new_product.price,
            "image": new_product.image,
        }
    }


@app.delete("/admin/products/{product_id}")
def delete_product(product_id: int, _=Depends(check_admin_key)):
    db = SessionLocal()
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()

    if not product:
        db.close()
        return {"status": "error", "message": "Товар не найден"}

    db.delete(product)
    db.commit()
    db.close()

    return {"status": "ok", "message": "Товар удалён"}


@app.post("/order")
def create_order(order: dict, user_id: Optional[int] = Depends(get_optional_user_id)):
    new_order = order.copy()

    # уникальный id
    new_order["id"] = int(time.time() * 1000)
    new_order["status"] = "new"
    new_order["created_at"] = int(time.time())

    # ссылка на админку на конкретный заказ (без admin key в URL)
    admin_link = None
    if FRONTEND_URL:
        admin_link = f"{FRONTEND_URL}/admin?order={new_order['id']}"

    items_text = "\n".join([
        f"• {item['title']} x{item['quantity']} = {item['price'] * item['quantity']} ₽"
        for item in new_order["items"]
    ])

    msg = (
        "🧱 <b>Новый заказ!</b>\n\n"
        f"🆔 ID: <code>{new_order['id']}</code>\n"
        f"👤 Имя: <b>{new_order.get('name')}</b>\n"
        f"📞 Телефон: <b>{new_order.get('phone')}</b>\n"
        f"🏠 Адрес: <b>{new_order.get('address', '-')}</b>\n\n"
        f"📦 Товары:\n{items_text}\n\n"
        f"💰 Итого: <b>{new_order.get('total')} ₽</b>"
    )

    if admin_link:
        msg += f"\n\n👉 <a href='{admin_link}'>Открыть заказ в админке</a>"

    send_telegram_message(msg)

    db = SessionLocal()

    db_order = OrderModel(
        id=new_order["id"],
        name=new_order.get("name"),
        phone=new_order.get("phone"),
        status=new_order.get("status"),
        total=new_order.get("total"),
        created_at=new_order.get("created_at"),
        user_id=user_id
    )

    db.add(db_order)
    db.commit()
    db.close()

    return {"status": "ok", "order_id": new_order["id"]}

@app.post("/admin/upload")
async def upload_image(
    file: UploadFile = File(...),
    x_admin_key: str = Header(None)
    ):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Only images allowed")

    content = await file.read()

    filename = f"{uuid.uuid4().hex}{ext}"

    # Загружаем в Supabase Storage
    supabase.storage.from_("product-images").upload(
        filename,
        content,
        {"content-type": file.content_type}
    )

    # Получаем публичный URL
    public_url = supabase.storage.from_("product-images").get_public_url(filename)

    return {
        "status": "ok",
        "filename": public_url
    }

@app.post("/auth/telegram/init")
def init_telegram_auth():
    db = SessionLocal()

    code = secrets.token_hex(16)

    session = AuthSessionModel(
        code=code,
        telegram_id=None,
        created_at=int(time.time()),
        used=False
    )

    db.add(session)
    db.commit()
    db.close()

    return {"code": code}


@app.get("/orders")
def get_orders(_=Depends(check_admin_key)):
    db = SessionLocal()
    db_orders = db.query(OrderModel).all()
    db.close()

    return [
        {
            "id": o.id,
            "name": o.name,
            "phone": o.phone,
            "status": o.status,
            "total": o.total,
            "created_at": o.created_at,
        }
        for o in db_orders
    ]

@app.get("/me")
def get_me(user_id: int = Depends(get_current_user_id)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "photo_url": user.photo_url,
            }
        }
    finally:
        db.close()

@app.get("/my/orders")
def get_my_orders(user_id: int = Depends(get_current_user_id)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = SessionLocal()
    try:
        orders = (
            db.query(OrderModel)
            .filter(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .all()
        )

        return {
            "orders": [
                {
                    "id": o.id,
                    "status": o.status,
                    "total": o.total,
                    "created_at": o.created_at,
                }
                for o in orders
            ]
        }
    finally:
        db.close()

from auth import create_jwt  # если JWT у тебя в auth.py

@app.get("/auth/telegram/check")
def check_telegram_auth(code: str):
    db = SessionLocal()

    session = db.query(AuthSessionModel).filter(
        AuthSessionModel.code == code
    ).first()

    if not session:
        db.close()
        return {"status": "not_found"}

    if session.telegram_id is None:
        db.close()
        return {"status": "pending"}

    # пользователь подтвердился в боте
    telegram_id = session.telegram_id

    # найти или создать user
    user = db.query(UserModel).filter(
        UserModel.telegram_id == telegram_id
    ).first()

    if not user:
        user = UserModel(
            telegram_id=telegram_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    session.used = True
    db.commit()
    db.close()

    token = create_jwt(user.id)

    return {
        "status": "ok",
        "token": token
    }



@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status: dict, _=Depends(check_admin_key)):
    new_status = status.get("status")

    allowed = ["new", "confirmed", "shipped", "done"]
    if new_status not in allowed:
        return {"status": "error", "message": "Неверный статус"}

    db = SessionLocal()
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

    if not order:
        db.close()
        return {"status": "error", "message": "Заказ не найден"}

    order.status = new_status
    db.commit()
    db.close()

    return {"status": "ok", "message": "Статус обновлён"}



@app.get("/public/orders/{order_id}")
def get_public_order(order_id: int):
    db = SessionLocal()
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

    if not order:
        db.close()
        raise HTTPException(status_code=404, detail="Order not found")

    result = {
        "id": order.id,
        "status": order.status,
        "created_at": order.created_at,
        "total": order.total,
        "items": []  # пока без items (мы их ещё не перенесли)
    }

    db.close()
    return result

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("TELEGRAM UPDATE:", data)

    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    text = message.get("text", "")
    chat_id = message["chat"]["id"]

    print("TEXT:", text)

    if text.startswith("/start web_"):
        code = text.replace("/start web_", "").strip()
        success = attach_telegram_to_session(code, chat_id)

        print("AUTH CODE:", code, "SUCCESS:", success)

        if success:
            send_telegram_reply(chat_id, "✅ Вы успешно авторизованы. Вернитесь на сайт.")
        else:
            send_telegram_reply(chat_id, "❌ Сессия устарела.")

    return {"ok": True}

