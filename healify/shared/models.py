from django.db import models
"""
class Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)  # Changed to AutoField
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    num_phone = models.CharField(max_length=20)  # Consider using a PhoneField if available
    sex = models.CharField(max_length=10)  # Consider using an EnumField with choices
    address = models.TextField()
    birth_date = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class History(models.Model):
    history_id = models.AutoField(primary_key=True) # Changed to AutoField.  history_id is already the PK
    date = models.DateField()
    time = models.TimeField()
    def __str__(self):
        return f"History {self.history_id} on {self.date} at {self.time}"
"""
