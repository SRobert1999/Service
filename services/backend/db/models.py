from tortoise import fields
from tortoise.models import Model

class Persoana(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)
    prenume = fields.CharField(max_length=100)

    class Meta:
        table = "Persoane"


class Serviciu(Model):
    id = fields.IntField(pk=True)
    descriere = fields.CharField(max_length=255)

    class Meta:
        table = "Servicii"


class Programari(Model):
    id = fields.IntField(pk=True)
    persoana = fields.ForeignKeyField("models.Persoana", related_name="programari", null=True)
    serviciu = fields.ForeignKeyField("models.Serviciu", related_name="programari", null=True)
    data = fields.CharField(max_length=50, null=True)
    observatii = fields.TextField(null=True)
    nume = fields.CharField(max_length=100, null=True)
    prenume = fields.CharField(max_length=100, null=True)
    email = fields.CharField(max_length=200, null=True)
    telefon = fields.CharField(max_length=50, null=True)

    class Meta:
        table = "Programari"