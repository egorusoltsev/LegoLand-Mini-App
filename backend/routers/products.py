from fastapi import APIRouter, Depends
from db import SessionLocal
from models import ProductModel
from auth.dependencies import check_admin_key

router = APIRouter()


@router.get("/products")
def get_products():
    db = SessionLocal()
    db_products = db.query(ProductModel).all()
    db.close()

    return [
        {"id": p.id, "title": p.title, "price": p.price, "image": p.image}
        for p in db_products
    ]


@router.post("/admin/products")
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
        },
    }


@router.delete("/admin/products/{product_id}")
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
