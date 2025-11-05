#!/usr/bin/env python3
"""
Script pentru aplicarea manuală a migrărilor
"""

import sqlite3
import os
import glob

def apply_migration():
    """Apply migration manually"""

    # Create database directory
    os.makedirs('/tmp/db', exist_ok=True)

    # Connect to database
    conn = sqlite3.connect('/tmp/db/programari.db')
    cursor = conn.cursor()

    # Create aerich table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "aerich" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "version" VARCHAR(255) NOT NULL,
            "app" VARCHAR(100) NOT NULL,
            "content" TEXT NOT NULL
        )
    """)

    # Get list of all migration files
    migration_files = sorted(glob.glob('/app/migrations/models/*.py'))

    for migration_file in migration_files:
        filename = migration_file.split('/')[-1]
        version = filename.replace('.py', '')

        # Check if migration already applied
        cursor.execute("SELECT version FROM aerich WHERE version = ?", (version,))
        if cursor.fetchone():
            print(f"Migration {version} already applied, skipping...")
            continue

        print(f"Applying migration: {version}")

        # Read migration file
        with open(migration_file, 'r') as f:
            content = f.read()

        # Extract SQL from upgrade function
        start_marker = '"""'
        end_marker = '"""'

        start_idx = content.find(start_marker, content.find('async def upgrade'))
        if start_idx == -1:
            print(f"Start marker not found in {version}")
            continue

        start_idx += len(start_marker)
        end_idx = content.find(end_marker, start_idx)

        if end_idx == -1:
            print(f"End marker not found in {version}")
            continue

        sql = content[start_idx:end_idx]

        print(f"Applying SQL for {version}...")

        try:
            cursor.executescript(sql)
            conn.commit()
            print(f"Migration {version} applied successfully!")

            # Insert migration record
            cursor.execute("""
                INSERT INTO aerich (version, app, content)
                VALUES (?, 'models', '{}')
            """, (version,))
            conn.commit()

        except Exception as e:
            print(f"Error applying migration {version}: {e}")
            return False

    # Verify final state
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Final tables: {[t[0] for t in tables]}")

    # Show applied migrations
    cursor.execute("SELECT version FROM aerich ORDER BY id;")
    applied = cursor.fetchall()
    print(f"Applied migrations: {[v[0] for v in applied]}")

    conn.close()
    return True

if __name__ == "__main__":
    success = apply_migration()
    exit(0 if success else 1)