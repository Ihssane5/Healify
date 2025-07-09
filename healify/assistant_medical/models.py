from django.db import models
from accounts.models import Patient  # Importer ton modèle Patient

class Conversation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, default='New conversation')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.patient.first_name}"
    
class Message(models.Model):
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    content = models.TextField(blank=True, null=True)  # Pour le texte
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)  # Pour les images
    message_type = models.CharField(max_length=10, choices=[('text', 'Text'),('image', 'Image'),], default='text')
    timestamp = models.DateTimeField(auto_now_add=True)
    diagnosis = models.JSONField(blank=True, null=True)  # Nouveau champ pour stocker le diagnostic

    def __str__(self):
        return f"{self.sender} - {self.message_type} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        if self.image and not self.content:
            self.message_type = 'image'
        super().save(*args, **kwargs)

