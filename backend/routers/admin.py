import os
import uuid
from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from supabase import create_client

router = APIRouter()


@router.post("/admin/upload")
async def upload_image(file: UploadFile = File(...), x_admin_key: str = Header(None)):
    admin_key = os.getenv("ADMIN_KEY")
    if x_admin_key != admin_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Only images allowed")

    content = await file.read()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise HTTPException(status_code=500, detail="Supabase env not set")

    supabase = create_client(supabase_url, supabase_key)

    filename = f"{uuid.uuid4().hex}{ext}"

    supabase.storage.from_("product-images").upload(
        filename, content, {"content-type": file.content_type}
    )

    public_url = supabase.storage.from_("product-images").get_public_url(filename)

    return {"status": "ok", "filename": public_url}
