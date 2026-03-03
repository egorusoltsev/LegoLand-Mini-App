import os

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "JWT_SECRET",
    "TG_BOT_TOKEN",
    "TG_CHAT_ID",
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "ADMIN_KEY",
]


def validate_required_env() -> None:
    missing = []
    for key in REQUIRED_ENV_VARS:
        value = os.getenv(key)
        if value is None or not str(value).strip():
            missing.append(key)

    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )
