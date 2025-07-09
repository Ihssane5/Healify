
from django.urls import path
from . import views  # Si tu as des vues à appeler

urlpatterns = [
    path('', views.home, name='home'), 
    path('login/', views.patient_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
]
