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

# CORS (обязательно для Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory="images"), name="images")

products = [
    {
        "id": 1,
        "title": "LEGO Star Wars X-Wing",
        "price": 12990,
        "image": "http://localhost:8000/images/Picture1forassets.jpg"
    },
    {
        "id": 2,
        "title": "LEGO Technic Bugatti",
        "price": 45990,
        "image": "http://localhost:8000/images/Picture2forassets.jpg"
    },
    {
        "id": 3,
        "title": "LEGO City Police Station",
        "price": 8990,
        "image": "http://localhost:8000/images/Picture3forassets.jpg"
    }
]


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