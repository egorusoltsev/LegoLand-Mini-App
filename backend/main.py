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

load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
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
    return products

@app.post("/admin/products")
def add_product(product: dict, _=Depends(check_admin_key)):
    # 1) генерируем новый id: берём максимальный существующий + 1
    new_id = 1
    if len(products) > 0:
        new_id = max(p.get("id", 0) for p in products) + 1

    # 2) создаём новый товар
    new_product = {
        "id": new_id,
        "title": product.get("title", ""),
        "price": product.get("price", 0),
        "image": product.get("image", "")
    }

    # 3) простая проверка (валидация)
    if not new_product["title"] or not new_product["image"]:
        return {"status": "error", "message": "title и image обязательны"}

    products.append(new_product)
    save_products(products)

    return {"status": "ok", "product": new_product}

@app.delete("/admin/products/{product_id}")
def delete_product(product_id: int, _=Depends(check_admin_key)):
    global products
    before = len(products)

    products = [p for p in products if p.get("id") != product_id]

    if len(products) == before:
        return {"status": "error", "message": "Товар не найден"}

    save_products(products)
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

    orders.append(new_order)
    save_orders(orders)

    return {"status": "ok", "order_id": new_order["id"]}

@app.post("/admin/upload")
async def upload_image(
    file: UploadFile = File(...),
    x_admin_key: str = Header(None)
):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    os.makedirs("images", exist_ok=True)

    # берём расширение
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Only images allowed")

    # безопасное уникальное имя файла
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join("images", filename)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    return {"status": "ok", "filename": filename, "url": f"/images/{filename}"}

@app.get("/orders")
def get_orders(_=Depends(check_admin_key)):
    return load_orders()

@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status: dict, _=Depends(check_admin_key)):
    new_status = status.get("status")

    allowed = ["new", "confirmed", "shipped", "done"]
    if new_status not in allowed:
        return {"status": "error", "message": "Неверный статус"}

    orders_list = load_orders()

    for order in orders_list:
        if order.get("id") == order_id:
            order["status"] = new_status
            save_orders(orders_list)
            return {"status": "ok", "message": "Статус обновлён"}

    return {"status": "error", "message": "Заказ не найден"}


@app.get("/public/orders/{order_id}")
def get_public_order(order_id: int):
    orders_list = load_orders()

    for o in orders_list:
        if o.get("id") == order_id:
            # отдаём только безопасные поля
            return {
                "id": o.get("id"),
                "status": o.get("status", "new"),
                "created_at": o.get("created_at"),
                "total": o.get("total", 0),
                "items": [
                    {
                        "title": i.get("title"),
                        "price": i.get("price"),
                        "quantity": i.get("quantity"),
                    }
                    for i in (o.get("items") or [])
                ],
            }

    raise HTTPException(status_code=404, detail="Order not found")
