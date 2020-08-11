from django.db import models


class Users(models.Model):
    email = models.CharField(primary_key=True, max_length=80)
    hashed_password = models.CharField(max_length=120)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'

