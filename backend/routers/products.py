from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from auth.dependencies import check_admin_key
from db import get_db
from models import ProductModel

router = APIRouter()


class ProductCreate(BaseModel):
    title: str = Field(min_length=1)
    price: int = Field(ge=0)
    image: str = Field(min_length=1)
    sku: Optional[str] = None
    pieces: Optional[int] = Field(default=None, ge=0)
    series: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

    @field_validator("title", "image")
    @classmethod
    def trimmed_required(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty")
        return cleaned


@router.get("/products")
def get_products(limit: int = 100, offset: int = 0, db=Depends(get_db)):
    db_products = db.query(ProductModel).offset(offset).limit(limit).all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "price": p.price,
            "image": p.image,
            "sku": p.sku,
            "pieces": p.pieces,
            "series": p.series,
            "description": p.description,
            "category": p.category,
        }
        for p in db_products
    ]


@router.post("/admin/products")
def add_product(product: ProductCreate, _=Depends(check_admin_key), db=Depends(get_db)):

    new_product = ProductModel(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "status": "ok",
        "product": {
            "id": new_product.id,
            "title": new_product.title,
            "price": new_product.price,
            "image": new_product.image,
            "sku": new_product.sku,
            "pieces": new_product.pieces,
            "series": new_product.series,
            "description": new_product.description,
            "category": new_product.category,
        },
    }


@router.delete("/admin/products/{product_id}")
def delete_product(product_id: int, _=Depends(check_admin_key), db=Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    db.delete(product)
    db.commit()
    return {"status": "ok", "message": "Товар удалён"}
