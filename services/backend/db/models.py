from tortoise import fields
from tortoise.models import Model

class Persoane(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)
    prenume = fields.CharField(max_length=100)

    class Meta:
        table = "Persoane"


class Servicii(Model):
    id = fields.IntField(pk=True)
    descriere = fields.CharField(max_length=255)

    class Meta:
        table = "Servicii"


class Programari(Model):
    id = fields.IntField(pk=True)
    persoana = fields.ForeignKeyField('models.Persoane', related_name='programari', null=True, on_delete=fields.CASCADE)
    serviciu = fields.ForeignKeyField('models.Servicii', related_name='programari', null=True, on_delete=fields.CASCADE)
    data = fields.CharField(max_length=50, null=True)
    ora = fields.CharField(max_length=10, null=True)
    observatii = fields.TextField(null=True)
    nume = fields.CharField(max_length=100, null=True)
    prenume = fields.CharField(max_length=100, null=True)
    email = fields.CharField(max_length=200, null=True)
    telefon = fields.CharField(max_length=50, null=True)

    class Meta:
        table = "Programari"