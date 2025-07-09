from django.shortcuts import render, redirect
from .forms import * 
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from functools import wraps
from django.shortcuts import redirect

def patient_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'current_patient_id' not in request.session:
            return redirect(f"/login/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    return render(request, 'index.html',{'title':"Home | Aesthetic"})


from django.contrib.auth import login as auth_login
from django.contrib.auth.models import AnonymousUser

def patient_login(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            patient = Patient.objects.get(email=email)
            # Enregistrer manuellement dans la session
            request.session['current_patient_id'] = patient.id
            return redirect(next_url if next_url else 'home')
    else:
        form = PatientLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form, 'title': "Login | Aesthetic"})



def register(request):
    if request.method == 'POST':
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.password = make_password(form.cleaned_data['password'])  # on hash le password
            patient.save()
            messages.success(request, "Registration successful")
            return redirect('login')
    else:
        form = PatientRegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'title':"Register | Aesthetic"})


def logout(request):
    if 'current_patient_id' in request.session:
        del request.session['current_patient_id']
    
    return redirect('home')

