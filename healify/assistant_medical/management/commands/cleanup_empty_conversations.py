# assistant_medical/management/commands/cleanup_empty_conversations.py
from django.core.management.base import BaseCommand
from assistant_medical.models import Conversation

class Command(BaseCommand):
    help = 'Supprime les conversations vides'

    def handle(self, *args, **options):
        # Supprime les conversations sans messages utilisateur
        empty_conversations = Conversation.objects.filter(
            messages__sender='user'
        ).exclude(
            messages__isnull=False
        ).distinct()
        
        count = empty_conversations.count()
        empty_conversations.delete()
        
        self.stdout.write(f'Supprimé {count} conversations vides')