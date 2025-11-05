from tortoise import fields
from tortoise.models import Model

class Users(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=200)
    email = fields.CharField(max_length=200, unique=True)
    role = fields.CharField(max_length=20, default='user')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "Users"

class Job(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100, unique=True)  # Standard snake_case
    # Fără created_at și updated_at

    class Meta:
        table = "Job"

class Persoane(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)
    prenume = fields.CharField(max_length=100)
    job = fields.ForeignKeyField('models.Job', related_name='persoane', null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = "Persoane"

class Servicii(Model):
    id = fields.IntField(pk=True)  # Standard snake_case
    descriere = fields.CharField(max_length=255)  # Standard snake_case
    job = fields.ForeignKeyField('models.Job', related_name='servicii', null=True, on_delete=fields.SET_NULL)
    # Fără created_at și updated_at

    class Meta:
        table = "Servicii"

class PersoanaJob(Model):
    id = fields.IntField(pk=True)
    persoana = fields.ForeignKeyField('models.Persoane', related_name='joburi_relation', on_delete=fields.CASCADE)
    job = fields.ForeignKeyField('models.Job', related_name='persoane_relation', on_delete=fields.CASCADE)
    # Fără created_at

    class Meta:
        table = "PersoanaJob"
        unique_together = [("persoana", "job")]

class Programari(Model):
    id = fields.IntField(pk=True)
    persoana = fields.ForeignKeyField('models.Persoane', related_name='programari', null=True, on_delete=fields.SET_NULL)
    job = fields.ForeignKeyField('models.Job', related_name='programari', null=True, on_delete=fields.SET_NULL)
    serviciu = fields.ForeignKeyField('models.Servicii', related_name='programari', null=True, on_delete=fields.SET_NULL)
    data = fields.DateField()  # Tip corect pentru date
    ora = fields.CharField(max_length=5)  # Format HH:MM
    observatii = fields.TextField(null=True)
    nume = fields.CharField(max_length=100, null=True)
    prenume = fields.CharField(max_length=100, null=True)
    email = fields.CharField(max_length=200, null=True)
    telefon = fields.CharField(max_length=20, null=True)


    class Meta:
        table = "Programari"