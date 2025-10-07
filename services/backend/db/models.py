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
    id = fields.IntField(pk=True, source_field='ID')
    persoana_id = fields.IntField(null=True, source_field='PersoanaId')
    serviciu_id = fields.IntField(null=True, source_field='ServiciuID')
    data = fields.CharField(max_length=50, null=True, source_field='Data')
    ora = fields.CharField(max_length=10, null=True, source_field='Ora')
    observatii = fields.TextField(null=True, source_field='Observatii')
    nume = fields.CharField(max_length=100, null=True, source_field='Nume')
    prenume = fields.CharField(max_length=100, null=True, source_field='Prenume')
    email = fields.CharField(max_length=200, null=True, source_field='Email')
    telefon = fields.CharField(max_length=50, null=True, source_field='Telefon')

    class Meta:
        table = "Programari"