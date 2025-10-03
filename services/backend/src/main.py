from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from pydantic import BaseModel
from db.models import Programari

app = FastAPI(title="rogramari API")

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
    persoana_id: int = None
    serviciu_id: int = None
    data: str = None
    observatii: str = None
    nume: str = None
    prenume: str = None
    email: str = None
    telefon: str = None


@app.get("/programari")
async def get_programari():
    programari = await Programari.all().values()
    return programari

@app.post("/programari")
async def create_programare(prog: ProgramareIn):
    p = await Programari.create(
        persoana_id=prog.persoana_id,
        serviciu_id=prog.serviciu_id,
        data=prog.data,
        observatii=prog.observatii,
        nume=prog.nume,
        prenume=prog.prenume,
        email=prog.email,
        telefon=prog.telefon
    )
    return {"status": "success", "id": p.id}


register_tortoise(
    app,
    db_url="sqlite:///app/db/programari.db",
    modules={"models": ["db.models"]},
    generate_schemas=False,
    add_exception_handlers=True,
)
