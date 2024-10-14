import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserDetails
from .models import Trabajador, ContactoEmergencia, CargaFamiliar
from datetime import date
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import modelformset_factory

from .models import Book
from .models import Review

# Formulario de inicio de sesión
class LoginForm(forms.Form):
    username = forms.CharField(label="RUT", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # Validación personalizada para el RUT
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        # Patrón para validar el formato "XXXXXXXX-X"
        pattern = r'^\d{8}-[\dkK]$'
        if not re.match(pattern, rut):
            raise ValidationError('El formato del RUT es inválido. El formato correcto es XXXXXXXX-X (8 números seguidos por un guion y finalizado con una "K" o un número).')
        return rut

    

class TrabajadorEditForm(forms.ModelForm): #EDITAR PERFIL
    class Meta:
        model = Trabajador
        fields = ['direccion', 'telefono']
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        # Verificar si el teléfono tiene exactamente 8 dígitos
        if not re.match(r'^\d{8}$', telefono):
            raise ValidationError('El formato del teléfono es inválido. El formato correcto es 12345678.')
        return telefono

class CustomPasswordChangeForm(PasswordChangeForm):
    pass  # Usar la lógica de cambio de contraseña predeterminada de Django

class TrabajadorFullEditForm(forms.ModelForm): #EDITAR ADMIN
    class Meta:
        model = Trabajador
        fields = ['rut', 'nombre', 'sexo', 'direccion', 'telefono', 'cargo', 'fecha_ingreso', 'area', 'departamento']
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),  # Widget de calendario
        }
    # Validación personalizada para evitar fechas futuras
    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        if fecha_ingreso > date.today():
            raise ValidationError("La fecha de ingreso no puede ser una fecha futura.")
        return fecha_ingreso
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        # Verificar si el teléfono tiene exactamente 8 dígitos
        if not re.match(r'^\d{8}$', telefono):
            raise ValidationError('El formato del teléfono es inválido. El formato correcto es 12345678.')
        return telefono

class ContactoEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ContactoEmergencia
        fields = ['nombre', 'relacion', 'telefono']
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        # Verificar si el teléfono tiene exactamente 8 dígitos
        if not re.match(r'^\d{8}$', telefono):
            raise ValidationError('El formato del teléfono es inválido. El formato correcto es 12345678.')
        return telefono
class CargaFamiliarForm(forms.ModelForm):
    class Meta:
        model = CargaFamiliar
        fields = ['nombre', 'parentesco', 'sexo', 'rut']
    # Validación personalizada para el RUT
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        # Patrón para validar el formato "XXXXXXXX-X"
        pattern = r'^\d{8}-[\dkK]$'
        if not re.match(pattern, rut):
            raise ValidationError('El formato del RUT es inválido. El formato correcto es XXXXXXXX-X (8 números seguidos por un guion y finalizado con una "K" o un número).')
        return rut

# Formulario para editar detalles adicionales del usuario
class UserDetailsForm(forms.ModelForm):
   class Meta:
       model = UserDetails
       fields = ['rol', 'fecha_nacimiento', 'fono', 'numero_doc', 'dv', 'pasaporte']


# Formulario de registro
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repite la contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    # Validación para confirmar que ambas contraseñas coinciden
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['password2']

class TrabajadorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    is_admin = forms.BooleanField(required=False, label='¿Es administrador?')
    
    class Meta:
        model = Trabajador
        fields = ['rut', 'nombre', 'sexo', 'direccion', 'telefono', 'cargo', 'fecha_ingreso', 'area', 'departamento']
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

    # Validar que la fecha de ingreso no sea futura
    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        if fecha_ingreso and fecha_ingreso > date.today():
            raise ValidationError('La fecha de ingreso no puede ser una fecha futura.')
        return fecha_ingreso

    # Validación personalizada para el RUT
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        # Patrón para validar el formato "XXXXXXXX-X"
        pattern = r'^\d{8}-[\dkK]$'
        if not re.match(pattern, rut):
            raise ValidationError('El formato del RUT es inválido. El formato correcto es XXXXXXXX-X (8 números seguidos por un guion y finalizado con una "K" o un número).')
        return rut

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        # Verificar si el teléfono tiene exactamente 8 dígitos
        if not re.match(r'^\d{8}$', telefono):
            raise ValidationError('El formato del teléfono es inválido. El formato correcto es 12345678.')
        return telefono

###
###DESACTUALIZADO VVVV
###

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'published_date', 'isbn']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }