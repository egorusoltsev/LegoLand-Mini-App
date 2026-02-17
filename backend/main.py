import json
import os
import time
import uuid
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from fastapi import Depends
from fastapi import Header, HTTPException
from fastapi import UploadFile, File
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from supabase import create_client


load_dotenv()

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

# CORS (обязательно для Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(Integer)
    image = Column(String)

Base.metadata.create_all(bind=engine)

ORDERS_FILE = "orders.json"

def check_admin_key(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
def save_orders(orders_list):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders_list, f, ensure_ascii=False, indent=2)
orders = load_orders()

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
def create_order(order: dict):
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
