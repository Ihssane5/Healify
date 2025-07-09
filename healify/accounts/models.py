from django.db import models
# app: accounts/models.py
class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    num_phone = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    address = models.TextField()
    sex = models.CharField(max_length=10)
    birth_date = models.DateField()
    def __str__(self):
        return f"{self.first_name} {self.last_name}"