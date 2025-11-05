#!/usr/bin/env python3
"""
Script final pentru a crea structura exactă conform modelelor Tortoise modificate
"""

import os
import sqlite3
import asyncio
from tortoise import Tortoise
from db.config import TORTOISE_ORM

async def create_final_structure():
    """
    Creează structura exactă conform modelelor Tortoise modificate
    """

    # Database path
    db_url = os.getenv("DATABASE_URL", "sqlite:///tmp/db/programari.db")
    db_path = db_url.replace("sqlite:///", "")

    print(f"Creating final database structure at: {db_path}")

    # Remove existing database completely
    if os.path.exists(db_path):
        os.remove(db_path)
    print("Removed existing database")

    # Initialize Tortoise and create schemas
    await Tortoise.init(config=TORTOISE_ORM)

    # This will create tables according to current models
    await Tortoise.generate_schemas(safe=False)

    print("Database structure created successfully!")

    # Verify structure
    print("\n=== VERIFICATION ===")

    # Connect directly to verify
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Created tables: {[t[0] for t in tables]}")

    print("\nDetailed structure:")

    # Check each important table
    for table_name in ['Job', 'Persoane', 'Servicii', 'PersoanaJob', 'Programari', 'Users']:
        print(f"\n{table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            nullable = "NULL" if col[3] == 0 else "NOT NULL"
            pk = "PK" if col[5] == 1 else ""
            print(f"  - {col[1]} {col[2]} {nullable} {pk}".strip())

    # Add initial record to aerich table
    cursor.execute("""
        INSERT OR REPLACE INTO aerich (id, version, app, content)
        VALUES (1, '1_20251103141033_None', 'models', '{}')
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO aerich (id, version, app, content)
        VALUES (2, '2_final_structure', 'models', '{}')
    """)
    conn.commit()

    print("\n✅ Aerich records added for migration tracking")

    conn.close()
    await Tortoise.close_connections()

    return True

if __name__ == "__main__":
    success = asyncio.run(create_final_structure())
    if success:
        print("\n✅ Final database structure created successfully!")
    else:
        print("\n❌ Error creating database structure!")
        exit(1)