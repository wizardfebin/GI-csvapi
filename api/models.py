from django.db import models

# Create your models here.
from django.db import models

# User model to store valid CSV records
class User(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)  # Unique constraint ensures duplicates are not allowed
    age = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"
