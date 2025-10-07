from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "Persoane" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "nume" VARCHAR(100) NOT NULL,
    "prenume" VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS "Servicii" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "descriere" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "Programari" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "data" VARCHAR(50),
    "ora" VARCHAR(10),
    "observatii" TEXT,
    "nume" VARCHAR(100),
    "prenume" VARCHAR(100),
    "email" VARCHAR(200),
    "telefon" VARCHAR(50),
    "persoana_id" INT REFERENCES "Persoane" ("id") ON DELETE CASCADE,
    "serviciu_id" INT REFERENCES "Servicii" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
