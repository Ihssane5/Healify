from django.db import models

from accounts.models import Patient
# Create your models here.

class History(models.Model):
    history_id = models.AutoField(primary_key=True) # Changed to AutoField.  history_id is already the PK
    date = models.DateField()
    time = models.TimeField()
    def __str__(self):
        return f"History {self.history_id} on {self.date} at {self.time}"
class MedicalRecord(models.Model):
    med_rec_id = models.AutoField(primary_key=True) # Changed to AutoField
    diagnosis = models.TextField()
    medical_analysis = models.TextField()  # Consider renaming to medical_analysis_text
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    history = models.ForeignKey(History, on_delete=models.CASCADE) # Corrected model name
    def __str__(self):
        return f"Record {self.med_rec_id} for {self.patient}"
    
class MedicalChat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    chat_summary = models.TextField()
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE)

    def __str__(self):
        return f"Medical Chat {self.chat_id}"
