#!/usr/bin/env python3
"""
Migrare pentru date de test inițiale
Această migrare adaugă datele de test în baza de date
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append('.')

from db.models import *
from tortoise import Tortoise
from datetime import date, timedelta
import bcrypt

async def upgrade():
    """
    Adaugă date de test inițiale în baza de date
    """
    # Initialize Tortoise pentru a putea folosi modelele
    db_url = os.getenv("DATABASE_URL", "sqlite:///tmp/db/programari.db")

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["db.models"]}
    )

    # Check if data already exists
    jobs_count = await Job.all().count()
    if jobs_count > 0:
        print(f"Test data already exists ({jobs_count} jobs), skipping...")
        await Tortoise.close_connections()
        return "Data already exists"

    # Jobs
    job1 = await Job.create(nume='Stomatolog')
    job2 = await Job.create(nume='Mecanic Auto')
    job3 = await Job.create(nume='Electrician')
    job4 = await Job.create(nume='Altele')
    job5 = await Job.create(nume='General/Ne-specificat')

    # Persoane
    pers1 = await Persoane.create(nume='Popescu', prenume='Ion', job=job1)
    pers2 = await Persoane.create(nume='Ionescu', prenume='Maria', job=job1)
    pers3 = await Persoane.create(nume='Stan', prenume='Radu', job=job2)
    pers4 = await Persoane.create(nume='Dumitru', prenume='Alexandru', job=job3)
    pers5 = await Persoane.create(nume='Gheorghe', prenume='Elena', job=job4)

    # Servicii
    serv1 = await Servicii.create(descriere='Consultatie generala', job=job1)
    serv2 = await Servicii.create(descriere='Extractie dentara', job=job1)
    serv3 = await Servicii.create(descriere='Tratament canal', job=job1)
    serv4 = await Servicii.create(descriere='Detartraj', job=job1)
    serv5 = await Servicii.create(descriere='Revizie tehnica', job=job2)
    serv6 = await Servicii.create(descriere='Schimbare ulei', job=job2)
    serv7 = await Servicii.create(descriere='Diagnoza electrica', job=job3)
    serv8 = await Servicii.create(descriere='Reparatii instalatii', job=job3)
    serv9 = await Servicii.create(descriere='Consultanta generala', job=job4)

    # PersoanaJob relationships - O persoană poate avea mai multe job-uri
    await PersoanaJob.create(persoana=pers1, job=job1)  # Popescu Ion -> Stomatolog
    await PersoanaJob.create(persoana=pers2, job=job1)  # Ionescu Maria -> Stomatolog
    await PersoanaJob.create(persoana=pers3, job=job2)  # Stan Radu -> Mecanic Auto
    await PersoanaJob.create(persoana=pers4, job=job3)  # Dumitru Alexandru -> Electrician
    await PersoanaJob.create(persoana=pers5, job=job4)  # Gheorghe Elena -> Altele

    # Exemplu: Persoană calificată în multiple domenii
    await PersoanaJob.create(persoana=pers1, job=job2)  # Popescu Ion -> Mecanic Auto (al doilea job)
    await PersoanaJob.create(persoana=pers3, job=job3)  # Stan Radu -> Electrician (al doilea job)

    # Sample appointments (future dates)
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    # Creează programări direct cu relații separate
    await Programari.create(
        data=tomorrow.isoformat(),
        ora='09:00',
        nume='Client Test 1',
        prenume='Test',
        email='client1@email.com',
        telefon='+40711234567',
        observatii='Programare la stomatolog',
        status='pending',
        persoana=pers1,  # Popescu Ion
        job=job1,       # Stomatolog
        serviciu=serv1  # Consultatie generala
    )

    await Programari.create(
        data=tomorrow.isoformat(),
        ora='10:30',
        nume='Client Test 2',
        prenume='Test',
        email='client2@email.com',
        telefon='+40712234567',
        observatii='Programare la mecanic auto',
        status='confirmed',
        persoana=pers1,  # Popescu Ion (calificat și ca mecanic)
        job=job2,       # Mecanic Auto
        serviciu=serv5  # Revizie tehnica
    )

    await Programari.create(
        data=next_week.isoformat(),
        ora='14:00',
        nume='Client Test 3',
        prenume='Test',
        email='client3@email.com',
        telefon='+40713234567',
        observatii='Programare electrician',
        status='pending',
        persoana=pers3,  # Stan Radu
        job=job3,       # Electrician
        serviciu=serv7  # Diagnoza electrica
    )

    # Add users
    password = 'parola123'
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    await Users.create(username='admin', password=hashed_password, email='admin@programari.ro', role='admin')
    await Users.create(username='user1', password=hashed_password, email='user1@programari.ro', role='user')
    await Users.create(username='user2', password=hashed_password, email='user2@programari.ro', role='user')

    await Tortoise.close_connections()

    return "Date de test adăugate cu succes"

async def downgrade():
    """
    Șterge datele de test (opțional)
    """
    # Initialize Tortoise pentru a putea folosi modelele
    db_url = os.getenv("DATABASE_URL", "sqlite:///tmp/db/programari.db")

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["db.models"]}
    )

    # Șterge toate datele
    await Programari.all().delete()
    await PersoanaJob.all().delete()
    await Users.all().delete()
    await Servicii.all().delete()
    await Persoane.all().delete()
    await Job.all().delete()

    await Tortoise.close_connections()

    return "Date de test șterse"

if __name__ == "__main__":
    asyncio.run(upgrade())