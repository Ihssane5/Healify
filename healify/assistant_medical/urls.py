
from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chatbot, name='chatbot'),
    path('save_message/', views.save_message, name='save_message'),
    path('delete_conversation/', views.delete_conversation, name='delete_conversation'),
    path('get_conversation_history/', views.get_conversation_history, name='get_conversation_history'),
    path('analyze_image/', views.analyze_image, name='analyze_image'),
]