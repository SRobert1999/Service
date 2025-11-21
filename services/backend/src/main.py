
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
from db.models import Programari, Persoane, Servicii, Job, PersoanaJob
from datetime import datetime, date
from fastapi.responses import JSONResponse

# Import auth routes
from src.routes import users
from src.auth.jwthandler import get_current_user

app = FastAPI(title="Programari API")

# enable schemas to read relationship between models
Tortoise.init_models(["db.models"], "models")  # NEW

origins = [
    "http://localhost:8080",   # frontend-ul Vue
    "http://127.0.0.1:8080"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include auth routes - authentication is optional for now
app.include_router(users.router, tags=["Authentication"])

async def filtreaza_programari_data_curenta():
    """
    Filtrează programările pentru a afișa doar cele din data curentă și viitoare.
    Programările din trecut rămân în baza de date dar nu sunt afișate.
    """
    try:
        azi = date.today()
        # Nu ștergem programările, doar le filtrăm la afișare
        return azi
    except Exception as e:
        print(f"Eroare la obținerea datei curente: {e}")
        return None


class ProgramareIn(BaseModel):
    # Câmpuri de bază cu validări
    data: str = Field(
        ...,
        description="Data programării în format YYYY-MM-DD",
        example="2025-10-15"
    )
    ora: str = Field(
        ...,
        description="Ora programării în format HH:MM",
        example="14:30"
    )

    # Foreign keys opționale (pentru compatibilitate temporară)
    persoana_id: Optional[int] = Field(
        None,
        ge=1,  # Greater than or equal to 1
        description="ID-ul persoanei din baza de date (compatibilitate)"
    )
    serviciu_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID-ul serviciului din baza de date (compatibilitate)"
    )

    # Date client opționale cu validări
    nume: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Numele clientului",
        example="Popescu"
    )
    prenume: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Prenumele clientului",
        example="Ion"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Adresa de email a clientului",
        example="ion.popescu@example.com"
    )
    telefon: Optional[str] = Field(
        None,
        pattern=r'^(\+4|0)[0-9]{9}$',  # Regex pentru telefon RO
        description="Număr de telefon românesc al clientului",
        example="+40712345678"
    )

    # Câmpuri suplimentare
    observatii: Optional[str] = Field(
        None,
        max_length=1000,
        description="Observații suplimentare",
        example="Client nou, preferă dimineața"
    )
    status: Optional[str] = Field(
        "pending",
        description="Statusul programării",
        example="pending"
    )

    # Compatibilitate cu frontend-ul vechi
    @property
    def nume_display(self):
        return getattr(self, 'nume', None)

    @property
    def prenume_display(self):
        return getattr(self, 'prenume', None)

    @property
    def email_display(self):
        return getattr(self, 'email', None)

    @property
    def telefon_display(self):
        return getattr(self, 'telefon', None)

    # Validatori personalizați
    @validator('data')
    def validate_data(cls, v):
        """Verifică că data este în format corect și nu e în trecut."""
        try:
            data_obj = datetime.strptime(v, '%Y-%m-%d')
            if data_obj.date() < datetime.now().date():
                raise ValueError('Data programării nu poate fi în trecut')
            return v
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError('Formatul datei trebuie să fie YYYY-MM-DD')
            raise e

    @validator('ora')
    def validate_ora(cls, v):
        """Verifică că ora este în format corect."""
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('Formatul orei trebuie să fie HH:MM (ex: 14:30)')

    # @validator('nume', 'prenume')
    # def validate_nume(cls, v):
    #     """Verifică că numele conține doar litere și spații."""
    #     if v and not all(c.isalpha() or c.isspace() for c in v):
    #         raise ValueError('Numele poate conține doar litere și spații')
    #     return v

    class Config:
        check_fields = False
        schema_extra = {
            "example": {
                "data": "2025-10-15",
                "ora": "14:30",
                "nume": "Popescu",
                "prenume": "Ion",
                "email": "ion.popescu@example.com",
                "telefon": "+40712345678"
            }
        }


@app.get("/")
async def root():
    """
    Health check endpoint.
    Returnează status-ul API-ului.
    """
    return {
        "status": "ok",
        "message": "Programari API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "programari": "/programari"
        }
    }

@app.get("/jobs")
async def get_jobs():
    jobs = await Job.all().values()
    return jobs

@app.get("/persoane")
async def get_persoane(job_id: Optional[int] = None):
    if job_id is not None:
        # Găsește persoanele calificate pentru acest job prin PersoanaJob
        persoane_job = await PersoanaJob.filter(job_id=job_id).prefetch_related('persoana')
        persoane_ids = [pj.persoana_id for pj in persoane_job]
        persoane = await Persoane.filter(id__in=persoane_ids).values()
    else:
        persoane = await Persoane.all().values()
    return persoane

@app.get("/servicii")
async def get_servicii(job_id: Optional[int] = None):
    if job_id is not None:
        servicii = await Servicii.filter(job_id=job_id).values()
    else:
        servicii = await Servicii.all().values()
    return servicii

@app.get("/programari")
async def get_programari(persoana_id: Optional[int] = None, job_id: Optional[int] = None):
   """
   Returnează programările din data curentă și viitoare.
   Poate filtra după persoana_id și/sau job_id.
   """
   # Obține data curentă pentru filtrare
   data_curenta = await filtreaza_programari_data_curenta()

   # Construiește filtrele
   filters = {}
   if data_curenta:
       filters['data__gte'] = data_curenta
   if persoana_id is not None:
       filters['persoana_id'] = persoana_id
   if job_id is not None:
       filters['job_id'] = job_id

   # Aplică filtrele
   if filters:
       programari = await Programari.filter(**filters).values()
       print(f"Displayed {len(programari)} appointments with filters: {filters}")
   else:
       programari = await Programari.all().values()
       print("Showing all appointments (no filters)")

   return programari


@app.post("/programari")
async def create_programare(prog: ProgramareIn):
    """
    Creează o programare nouă cu structura actualizată.
    O persoană poate avea multiple job-uri, iar programarea se face pentru un job specific.
    """
    try:
        # Pregătește datele pentru structura actuală
        programare_data = {
            "data": prog.data,
            "ora": prog.ora,
            "observatii": prog.observatii,
            "nume": prog.nume,
            "prenume": prog.prenume,
            "email": prog.email,
            "telefon": prog.telefon
        }

        # Adaugă relațiile directe
        if prog.persoana_id is not None:
            programare_data["persoana_id"] = prog.persoana_id
        if prog.serviciu_id is not None:
            programare_data["serviciu_id"] = prog.serviciu_id

        # Determină job-ul pe baza serviciului selectat
        if prog.serviciu_id is not None:
            serviciu = await Servicii.get_or_none(id=prog.serviciu_id)
            if serviciu:
                programare_data["job_id"] = serviciu.job_id

        # Creează programarea
        p = await Programari.create(**programare_data)
        return {"status": "success", "id": p.id, "message": "Programare creată cu succes"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la crearea programării: {str(e)}")


@app.delete("/programari/{programare_id}")
async def delete_programare(programare_id: int, current_user = Depends(get_current_user)):
    """
    Șterge o programare (doar pentru utilizatori autentificați).
    """
    try:
        programare = await Programari.get_or_none(id=programare_id)
        if not programare:
            raise HTTPException(status_code=404, detail="Programarea nu a fost găsită")

        await programare.delete()
        return {"status": "success", "message": "Programare ștearsă cu succes"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la ștergerea programării: {str(e)}")


@app.put("/programari/{programare_id}")
async def update_programare(programare_id: int, prog: ProgramareIn, current_user = Depends(get_current_user)):
    """
    Actualizează o programare (doar pentru utilizatori autentificați).
    """
    try:
        programare = await Programari.get_or_none(id=programare_id)
        if not programare:
            raise HTTPException(status_code=404, detail="Programarea nu a fost găsită")

        # Update programare data
        update_data = {
            "data": prog.data,
            "ora": prog.ora,
            "observatii": prog.observatii,
            "nume": prog.nume,
            "prenume": prog.prenume,
            "email": prog.email,
            "telefon": prog.telefon
        }

        # Adaugă foreign keys doar dacă sunt specificate
        if prog.persoana_id is not None:
            update_data["persoana_id"] = prog.persoana_id
        if prog.serviciu_id is not None:
            update_data["serviciu_id"] = prog.serviciu_id

        await programare.update_from_dict(update_data)
        await programare.save()

        return {"status": "success", "message": "Programare actualizată cu succes"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la actualizarea programării: {str(e)}")


import os
from pathlib import Path

# Use DATABASE_URL from environment
db_url = os.getenv("DATABASE_URL", "sqlite:///tmp/db/programari.db")

register_tortoise(
    app,
    db_url=db_url,
    modules={"models": ["db.models"]},
    generate_schemas=True,  # Generate schemas from models
    add_exception_handlers=True,
)
