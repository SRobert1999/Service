from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "Job" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "nume" VARCHAR(100) NOT NULL UNIQUE,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_Job_nume_1b66a2" ON "Job" ("nume");
CREATE TABLE IF NOT EXISTS "Persoane" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "nume" VARCHAR(100) NOT NULL,
    "prenume" VARCHAR(100) NOT NULL,
    "email" VARCHAR(200)  UNIQUE,
    "telefon" VARCHAR(50),
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "job_id" INT REFERENCES "Job" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_Persoane_job_id_58d8bb" ON "Persoane" ("job_id");
CREATE INDEX IF NOT EXISTS "idx_Persoane_nume_b0ad65" ON "Persoane" ("nume", "prenume");
CREATE TABLE IF NOT EXISTS "PersoanaJob" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "job_id" INT NOT NULL REFERENCES "Job" ("id") ON DELETE CASCADE,
    "persoana_id" INT NOT NULL REFERENCES "Persoane" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_PersoanaJob_persoan_7751e2" UNIQUE ("persoana_id", "job_id")
);
CREATE INDEX IF NOT EXISTS "idx_PersoanaJob_persoan_376d9f" ON "PersoanaJob" ("persoana_id");
CREATE INDEX IF NOT EXISTS "idx_PersoanaJob_job_id_1a24cd" ON "PersoanaJob" ("job_id");
CREATE TABLE IF NOT EXISTS "Servicii" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "descriere" VARCHAR(255) NOT NULL,
    "durata_min" INT NOT NULL  DEFAULT 30,
    "pret" VARCHAR(40),
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "job_id" INT REFERENCES "Job" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_Servicii_job_id_87a4e7" ON "Servicii" ("job_id");
CREATE INDEX IF NOT EXISTS "idx_Servicii_descrie_a80feb" ON "Servicii" ("descriere");
CREATE TABLE IF NOT EXISTS "Programari" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "data" DATE NOT NULL,
    "ora" TIME NOT NULL,
    "observatii" TEXT,
    "nume_client" VARCHAR(100),
    "prenume_client" VARCHAR(100),
    "email_client" VARCHAR(200),
    "telefon_client" VARCHAR(50),
    "status" VARCHAR(20) NOT NULL  DEFAULT 'pending',
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "job_id" INT REFERENCES "Job" ("id") ON DELETE SET NULL,
    "persoana_id" INT REFERENCES "Persoane" ("id") ON DELETE SET NULL,
    "serviciu_id" INT REFERENCES "Servicii" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_Programari_data_3d8abf" ON "Programari" ("data");
CREATE INDEX IF NOT EXISTS "idx_Programari_data_730257" ON "Programari" ("data", "status");
CREATE INDEX IF NOT EXISTS "idx_Programari_persoan_400f77" ON "Programari" ("persoana_id");
CREATE INDEX IF NOT EXISTS "idx_Programari_job_id_d041f7" ON "Programari" ("job_id");
CREATE INDEX IF NOT EXISTS "idx_Programari_servici_de5b1a" ON "Programari" ("serviciu_id");
CREATE TABLE IF NOT EXISTS "Users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "password" VARCHAR(200) NOT NULL,
    "email" VARCHAR(200) NOT NULL UNIQUE,
    "role" VARCHAR(20) NOT NULL  DEFAULT 'user',
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
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
