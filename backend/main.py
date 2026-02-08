import json
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from fastapi import Depends
from fastapi import Header, HTTPException

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
ADMIN_KEY = "12345"

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

    # уникальный id (по времени, этого достаточно для MVP)
    new_order["id"] = int(time.time() * 1000)
    new_order["status"] = "new"

    orders.append(new_order)
    save_orders(orders)

    return {"status": "ok", "order_id": new_order["id"]}

@app.get("/orders")
def get_orders(_=Depends(check_admin_key)):
    return orders

@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status: dict, _=Depends(check_admin_key)):
    new_status = status.get("status")

    allowed = ["new", "confirmed", "shipped", "done"]
    if new_status not in allowed:
        return {"status": "error", "message": "Неверный статус"}

    for order in orders:
        if order.get("id") == order_id:
            order["status"] = new_status
            save_orders(orders)
            return {"status": "ok", "message": "Статус обновлён"}

    return {"status": "error", "message": "Заказ не найден"}