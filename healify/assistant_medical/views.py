from django.shortcuts import render, redirect, get_object_or_404
from accounts.views import patient_login_required
from .models import Conversation, Message
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from django.utils import timezone
import markdown as md
from django.utils.safestring import mark_safe
from django.db.models import Exists, OuterRef
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from datetime import datetime
from .predictor import predictor
from django.conf import settings


@patient_login_required
def chatbot(request):
    patient_id = request.session.get('current_patient_id')
    if not patient_id:
        return redirect('login')

    # Récupérer les conversations existantes
    conversations = Conversation.objects.filter(
        patient_id=patient_id
    ).annotate(
        has_user_messages=Exists(Message.objects.filter(
            conversation=OuterRef('pk'),
            sender='user'
        ))
    ).filter(has_user_messages=True).order_by('-created_at')

    # Gestion nouvelle conversation
    if 'new_chat' in request.GET:
        current_conversation = Conversation.objects.create(
            patient_id=patient_id,
            title="Nouvelle conversation"
        )
        # Ajouter le message initial du bot
        Message.objects.create(
            conversation=current_conversation,
            sender='bot',
            content="Hi, I'm your medical assistant. How may I help you today?",
            message_type='text'
        )
        return redirect(f'{request.path}?conversation={current_conversation.id}')
    

    # Récupérer la conversation courante
    conversation_id = request.GET.get('conversation')
    if conversation_id:
        current_conversation = get_object_or_404(Conversation, id=conversation_id, patient_id=patient_id)
    else:
        # Si aucune conversation existante avec des messages utilisateur, créer une nouvelle
        current_conversation = conversations.first()
        if not current_conversation:
            current_conversation = Conversation.objects.create(
                patient_id=patient_id,
                title=f"Conversation du {timezone.now().strftime('%d/%m/%Y %H:%M')}"
            )

    # Préparer les messages pour le template
    messages_data = []
    if current_conversation:
        for msg in current_conversation.messages.all().order_by('timestamp'):
            content = msg.content
            if msg.sender == 'bot':
                content = md.markdown(content)
            
            messages_data.append({
                'sender': msg.sender,
                'content': mark_safe(content),
                'is_image': msg.message_type == 'image',
                'image_url': msg.image.url if msg.image and msg.image.url else None,
                'timestamp': msg.timestamp.strftime('%H:%M')
            })

    return render(request, 'assistant_medical/chatbot.html', {
        'title': 'AI Health Support',
        'conversations': conversations,
        'current_conversation': current_conversation,
        'messages': messages_data
    })

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
@csrf_exempt
@require_POST
@patient_login_required
@csrf_exempt
@require_POST
@patient_login_required
def save_message(request):
    try:
        # Gestion des images
        if request.FILES.get('image'):
            image_file = request.FILES['image']
            patient_id = request.session.get('current_patient_id')
            conversation_id = request.POST.get('conversation_id')
            
            # Créer ou récupérer la conversation
            if conversation_id:
                conversation = get_object_or_404(Conversation, id=conversation_id, patient_id=patient_id)
            else:
                conversation = Conversation.objects.create(
                    patient_id=patient_id,
                    title=f"Diagnostic du {datetime.now().strftime('%d/%m/%Y')}"
                )
            
            # Sauvegarder l'image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{image_file.name}"
            file_path = os.path.join('chat_images', str(patient_id), filename)
            
            # Créer le dossier si nécessaire
            os.makedirs(os.path.dirname(default_storage.path(file_path)), exist_ok=True)
            
            # Sauvegarder le fichier
            saved_path = default_storage.save(file_path, ContentFile(image_file.read()))
            
            # Créer le message avec l'image
            message = Message.objects.create(
                conversation=conversation,
                sender='user',
                message_type='image',
                image=saved_path,
                content=""  # Champ obligatoire mais vide
            )

            return JsonResponse({
                'status': 'success',
                'message_id': message.id,
                'image_url': default_storage.url(saved_path),
                'image_path': saved_path  # Nous en aurons besoin pour le traitement
            })
        
        data = json.loads(request.body)
        patient_id = request.session.get('current_patient_id')
        
        if not data.get('conversation_id'):
            # Création nouvelle conversation avec message initial
            conversation = Conversation.objects.create(
                patient_id=patient_id,
                title="Nouvelle conversation"
            )
            Message.objects.create(
                conversation=conversation,
                sender='bot',
                content="Hi, I'm your medical assistant. How may I help you today?",
                message_type='text'
            )
        else:
            conversation = Conversation.objects.get(
                id=data.get('conversation_id'),
                patient_id=patient_id
            )
        
        # Créer le message
        message = Message.objects.create(
            conversation=conversation,
            sender=data.get('sender'),
            content=data.get('content'),
            message_type=data.get('message_type', 'text')
        )
        
        # Mettre à jour le titre si c'est le premier message utilisateur
        if data.get('sender') == 'user':
            if not conversation.messages.filter(sender='user').exists():
                # Premier message utilisateur - créer un titre basé sur le contenu
                title = data.get('content')[:50]
                if len(data.get('content')) > 50:
                    title += "..."
                conversation.title = title
                conversation.save()
            elif conversation.title == "Nouvelle conversation":
                # Si c'était une nouvelle conversation, mettre à jour le titre
                title = data.get('content')[:50]
                if len(data.get('content')) > 50:
                    title += "..."
                conversation.title = title
                conversation.save()
        
        return JsonResponse({
            'status': 'success',
            'message_id': message.id,
            'conversation_id': conversation.id,
            'timestamp': message.timestamp.strftime('%H:%M')
        })
        
    except Exception as e:
        if 'conversation' in locals() and conversation.messages.count() == 0:
            conversation.delete()
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    

@csrf_exempt
@require_POST
@patient_login_required
def analyze_image(request):
    try:
        data = json.loads(request.body)
        image_path = data.get('image_path')
        message_id = data.get('message_id')
        
        # 1. Prédiction avec votre modèle
        full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
        diagnosis = predictor.predict(full_image_path)
        
        # 2. Appel à DeepSeek
        try:
            deepseek_response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {settings.OPENROUTER_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek/deepseek-r1:free',
                    'messages': [{
                        'role': 'user',
                        'content': f"Provide concise medical information about {diagnosis['class']} in English."
                    }]
                },
                timeout=15
            )
            medical_info = deepseek_response.json()['choices'][0]['message']['content']
        except Exception as e:
            medical_info = f"⚠️ Additional information unavailable (Error: {str(e)})"
        
        # Récupérer le message original
        message = Message.objects.get(id=message_id)
        
        # Créer le message de réponse
        bot_message = Message.objects.create(
            conversation=message.conversation,
            sender='bot',
            content=f"🔍 Analysis of your image:\nCondition: {diagnosis['class']}\nConfidence: {diagnosis['confidence']}%\n\n{medical_info}",
            message_type='text',
            diagnosis={
                'condition': diagnosis['class'],
                'confidence': float(diagnosis['confidence']),
                'medical_info': medical_info
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'diagnosis': bot_message.diagnosis
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    
@patient_login_required
def get_conversation_history(request):
    conversation_id = request.GET.get('conversation_id')
    patient_id = request.session.get('current_patient_id')
    
    conversation = get_object_or_404(Conversation, id=conversation_id, patient_id=patient_id)
    messages = conversation.messages.all().order_by('timestamp')
    
    history = [
        {
            'sender': msg.sender,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        }
        for msg in messages
    ]
    
    return JsonResponse({'messages': history})
    

from django.views.decorators.http import require_http_methods

@require_http_methods(["DELETE"])
@patient_login_required
def delete_conversation(request):
    try:
        conversation_id = request.GET.get('id')
        patient_id = request.session.get('current_patient_id')
        
        conversation = get_object_or_404(Conversation, id=conversation_id, patient_id=patient_id)
        conversation.delete()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)