from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
from db.models import Programari

app = FastAPI(title="Programari API")

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

    # Foreign keys opționale
    persoana_id: Optional[int] = Field(
        None,
        ge=1,  # Greater than or equal to 1
        description="ID-ul persoanei din baza de date"
    )
    serviciu_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID-ul serviciului din baza de date"
    )

    # Date personale opționale cu validări
    nume: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Numele persoanei",
        example="Popescu"
    )
    prenume: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Prenumele persoanei",
        example="Ion"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Adresa de email",
        example="ion.popescu@example.com"
    )
    telefon: Optional[str] = Field(
        None,
        pattern=r'^(\+4|0)[0-9]{9}$',  # Regex pentru telefon RO
        description="Număr de telefon românesc",
        example="+40712345678"
    )
    observatii: Optional[str] = Field(
        None,
        max_length=1000,
        description="Observații suplimentare",
        example="Pacient nou, preferă dimineața"
    )

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

    @validator('nume', 'prenume')
    def validate_nume(cls, v):
        """Verifică că numele conține doar litere și spații."""
        if v and not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError('Numele poate conține doar litere și spații')
        return v

    class Config:
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

@app.get("/programari")
async def get_programari():
   programari = await Programari.all().values()
   return programari



@app.post("/programari")
async def create_programare(prog: ProgramareIn):
    # Create programare - Tortoise adaugă automat _id la ForeignKey fields
    programare_data = {
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
        programare_data["persoana_id"] = prog.persoana_id
    if prog.serviciu_id is not None:
        programare_data["serviciu_id"] = prog.serviciu_id

    p = await Programari.create(**programare_data)
    return {"status": "success", "id": p.id}


register_tortoise(
    app,
    db_url="sqlite:///app/db/programari.db",
    modules={"models": ["db.models"]},
    generate_schemas=False,
    add_exception_handlers=True,
)
