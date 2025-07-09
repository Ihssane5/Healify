from django import forms
from .models import Patient

class PatientRegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'email', 'num_phone', 'password', 'address', 'sex', 'birth_date']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        # Vérifie si l'email existe déjà
        email = cleaned_data.get("email")
        if Patient.objects.filter(email=email).exists():
            self.add_error('email', "Email already exists.")

        return cleaned_data
    
class PatientLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                patient = Patient.objects.get(email=email)
                from django.contrib.auth.hashers import check_password
                if not check_password(password, patient.password):
                    self.add_error('password', "Incorrect password.")
            except Patient.DoesNotExist:
                self.add_error('email', "No account found with this email.")
        
        return cleaned_data

