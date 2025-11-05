import os
from pathlib import Path

# Use DATABASE_URL from environment or fallback to file path
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tmp/db/programari.db")

if DATABASE_URL.startswith("sqlite:///"):
    # Extract path from DATABASE_URL for Tortoise
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        # If relative path, make it absolute
        BASE_DIR = Path(__file__).parent.parent
        db_path = str(BASE_DIR / db_path)
    db_url = f"sqlite:///{db_path}"
else:
    db_url = DATABASE_URL

TORTOISE_ORM = {
    "connections": {
        "default": db_url
    },
    "apps": {
        "models": {
            "models": [
                "db.models", "aerich.models"
            ],
            "default_connection": "default"
        }
    }
}