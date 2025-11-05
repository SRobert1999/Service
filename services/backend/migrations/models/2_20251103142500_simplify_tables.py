from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Elimină coloanele suplimentare din Persoane
        CREATE TABLE "new_Persoane" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "nume" VARCHAR(100) NOT NULL,
            "prenume" VARCHAR(100) NOT NULL,
            "job_id" INT REFERENCES "Job" ("id") ON DELETE SET NULL
        );

        -- Copiază datele din tabela veche
        INSERT INTO "new_Persoane" (id, nume, prenume, job_id)
        SELECT id, nume, prenume, job_id FROM "Persoane";

        -- Șterge tabela veche și redenumește cea nouă
        DROP TABLE "Persoane";
        ALTER TABLE "new_Persoane" RENAME TO "Persoane";

        -- Recreează indecșii
        CREATE INDEX IF NOT EXISTS "idx_Persoane_job_id_58d8bb" ON "Persoane" ("job_id");
        CREATE INDEX IF NOT EXISTS "idx_Persoane_nume_b0ad65" ON "Persoane" ("nume", "prenume");

        -- Elimină coloanele suplimentare din Servicii
        CREATE TABLE "new_Servicii" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "descriere" VARCHAR(255) NOT NULL,
            "job_id" INT REFERENCES "Job" ("id") ON DELETE SET NULL
        );

        -- Copiază datele din tabela veche
        INSERT INTO "new_Servicii" (id, descriere, job_id)
        SELECT id, descriere, job_id FROM "Servicii";

        -- Șterge tabela veche și redenumește cea nouă
        DROP TABLE "Servicii";
        ALTER TABLE "new_Servicii" RENAME TO "Servicii";

        -- Recreează indecșii
        CREATE INDEX IF NOT EXISTS "idx_Servicii_job_id_87a4e7" ON "Servicii" ("job_id");
        CREATE INDEX IF NOT EXISTS "idx_Servicii_descrie_a80feb" ON "Servicii" ("descriere");
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Recreează Persoane cu coloanele suplimentare
        CREATE TABLE "new_Persoane" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "nume" VARCHAR(100) NOT NULL,
            "prenume" VARCHAR(100) NOT NULL,
            "email" VARCHAR(200)  UNIQUE,
            "telefon" VARCHAR(50),
            "job_id" INT REFERENCES "Job" ("id") ON DELETE SET NULL,
            "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
        );

        INSERT INTO "new_Persoane" (id, nume, prenume, job_id)
        SELECT id, nume, prenume, job_id FROM "Persoane";

        DROP TABLE "Persoane";
        ALTER TABLE "new_Persoane" RENAME TO "Persoane";

        -- Recreează Servicii cu coloanele suplimentare
        CREATE TABLE "new_Servicii" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "descriere" VARCHAR(255) NOT NULL,
            "durata_min" INT NOT NULL  DEFAULT 30,
            "pret" VARCHAR(40),
            "job_id" INT REFERENCES "Job" ("id") ON DELETE SET NULL,
            "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
        );

        INSERT INTO "new_Servicii" (id, descriere, job_id)
        SELECT id, descriere, job_id FROM "Servicii";

        DROP TABLE "Servicii";
        ALTER TABLE "new_Servicii" RENAME TO "Servicii";
    """