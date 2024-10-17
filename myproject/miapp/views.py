from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import user_passes_test
from django.forms import modelformset_factory

from miapp.models import UserDetails
from .forms import TrabajadorFullEditForm, TrabajadorEditForm, ContactoEmergenciaForm, CargaFamiliarForm
from .models import Trabajador, ContactoEmergencia, CargaFamiliar
from .forms import LoginForm, UserRegistrationForm
from django.contrib import messages
from .forms import TrabajadorForm

from .models import Book
from .forms import BookForm
from .models import Review
from .forms import ReviewForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']  # Usar el RUT como nombre de usuario
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirigir a la página principal después de iniciar sesión
            else:
                messages.error(request, 'RUT o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
   logout(request)
   return redirect('login')

@login_required
def home(request):
   return render(request, 'home.html')

@login_required
def user_list(request):
   if request.user.userdetails.rol != 'admin':
       messages.error(request, 'You do not have permission to view this page')
       return redirect('home')
   users = User.objects.all()
   return render(request, 'user_list.html', {'users': users})

@login_required
def user_edit(request):
    trabajador = request.user.trabajador

    if request.method == 'POST':
        trabajador_form = TrabajadorEditForm(request.POST, instance=trabajador)
        contacto_form = ContactoEmergenciaForm(request.POST, instance=trabajador.contactos_emergencia.first(), prefix='contacto')
        carga_familiar_form = CargaFamiliarForm(request.POST, instance=trabajador.cargas_familiares.first(), prefix='carga')
        password_form = PasswordChangeForm(user=request.user, data=request.POST)  # Agregar formulario de cambio de contraseña

        if trabajador_form.is_valid() and contacto_form.is_valid() and carga_familiar_form.is_valid() and password_form.is_valid():
            trabajador_form.save()

            # Guardar Contacto de Emergencia
            contacto = contacto_form.save(commit=False)
            contacto.trabajador = trabajador
            contacto.save()

            # Guardar Carga Familiar
            carga_familiar = carga_familiar_form.save(commit=False)
            carga_familiar.trabajador = trabajador
            carga_familiar.save()

            # Guardar la nueva contraseña
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Mantener la sesión activa

            messages.success(request, 'Tu perfil ha sido actualizado con éxito.')
            return redirect('home')
    else:
        trabajador_form = TrabajadorEditForm(instance=trabajador)
        contacto_form = ContactoEmergenciaForm(instance=trabajador.contactos_emergencia.first(), prefix='contacto')
        carga_familiar_form = CargaFamiliarForm(instance=trabajador.cargas_familiares.first(), prefix='carga')
        password_form = PasswordChangeForm(user=request.user)  # Mostrar formulario de cambio de contraseña

    return render(request, 'user_edit.html', {
        'trabajador_form': trabajador_form,
        'contacto_form': contacto_form,
        'carga_familiar_form': carga_familiar_form,
        'password_form': password_form,  # Enviar formulario de contraseña a la plantilla
    })

@login_required
def editar_trabajador(request, pk):
    trabajador = get_object_or_404(Trabajador, pk=pk)
    if request.method == 'POST':
        form = TrabajadorFullEditForm(request.POST, instance=trabajador)
        if form.is_valid():
            form.save()
            return redirect('listar_empleados')
    else:
        form = TrabajadorFullEditForm(instance=trabajador)
    return render(request, 'editar_trabajador.html', {'form': form})

@login_required
def eliminar_trabajador(request, pk):
    trabajador = get_object_or_404(Trabajador, pk=pk)

    # Verificar si el trabajador que intenta eliminar es el mismo usuario autenticado
    if request.user == trabajador.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('listar_empleados')

    if request.method == 'POST':
        trabajador.delete()
        messages.success(request, 'Trabajador eliminado con éxito.')
        return redirect('listar_empleados')
    
    return render(request, 'eliminar_trabajador.html', {'trabajador': trabajador})

@login_required
def editar_contacto_emergencia(request, pk):
    contacto = get_object_or_404(ContactoEmergencia, pk=pk)
    if request.method == 'POST':
        form = ContactoEmergenciaForm(request.POST, instance=contacto)
        if form.is_valid():
            form.save()
            return redirect('listar_empleados')
    else:
        form = ContactoEmergenciaForm(instance=contacto)
    return render(request, 'editar_contacto_emergencia.html', {'form': form})

@login_required
def editar_carga_familiar(request, pk):
    carga_familiar = get_object_or_404(CargaFamiliar, pk=pk)

    if request.method == 'POST':
        form = CargaFamiliarForm(request.POST, instance=carga_familiar)
        if form.is_valid():
            form.save()
            return redirect('listar_empleados')
    else:
        form = CargaFamiliarForm(instance=carga_familiar)

    return render(request, 'editar_carga_familiar.html', {'form': form})

@login_required
def user_delete(request, user_id):
   if request.user.userdetails.rol != 'admin':
       messages.error(request, 'You do not have permission to delete users')
       return redirect('home')

   user = get_object_or_404(User, id=user_id)
   if request.method == 'POST':
       user.delete()
       messages.success(request, 'User deleted successfully')
       return redirect('user_list')

   return render(request, 'user_delete.html', {'user': user})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Crear el usuario pero no lo guarda en la base de datos aún
            new_user = form.save(commit=False)
            # Establecer la contraseña
            new_user.set_password(form.cleaned_data['password'])
            # Guardar el usuario en la base de datos
            new_user.save()

            # Crear el detalle adicional del usuario
            UserDetails.objects.create(user=new_user)

            messages.success(request, 'El usuario se ha registrado exitosamente.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
@login_required
def listar_trabajadores(request):
    trabajadores = Trabajador.objects.all()
    return render(request, 'listar_trabajadores.html', {'trabajadores': trabajadores})

@login_required
def filtrar_trabajadores(request):
    trabajadores = Trabajador.objects.all()

    sexo = request.GET.get('sexo')
    cargo = request.GET.get('cargo')
    area = request.GET.get('area')

    if sexo:
        trabajadores = trabajadores.filter(sexo=sexo)
    if cargo:
        trabajadores = trabajadores.filter(cargo=cargo)
    if area:
        trabajadores = trabajadores.filter(area=area)

    return render(request, 'filtrar_trabajadores.html', {'trabajadores': trabajadores})

@user_passes_test(is_admin)
@login_required
def agregar_empleado(request):
    ContactoEmergenciaFormSet = modelformset_factory(ContactoEmergencia, form=ContactoEmergenciaForm, extra=1)
    CargaFamiliarFormSet = modelformset_factory(CargaFamiliar, form=CargaFamiliarForm, extra=1)

    if request.method == 'POST':
        trabajador_form = TrabajadorForm(request.POST)
        contacto_formset = ContactoEmergenciaFormSet(request.POST, queryset=ContactoEmergencia.objects.none())
        carga_familiar_formset = CargaFamiliarFormSet(request.POST, queryset=CargaFamiliar.objects.none())

        if trabajador_form.is_valid() and contacto_formset.is_valid() and carga_familiar_formset.is_valid():
            trabajador = trabajador_form.save()

            # Guardar Contactos de Emergencia
            for contacto_form in contacto_formset:
                contacto = contacto_form.save(commit=False)
                contacto.trabajador = trabajador
                contacto.save()

            # Guardar Cargas Familiares
            for carga_form in carga_familiar_formset:
                carga = carga_form.save(commit=False)
                carga.trabajador = trabajador
                carga.save()

            return redirect('listar_empleados')
    else:
        trabajador_form = TrabajadorForm()
        contacto_formset = ContactoEmergenciaFormSet(queryset=ContactoEmergencia.objects.none())
        carga_familiar_formset = CargaFamiliarFormSet(queryset=CargaFamiliar.objects.none())

    return render(request, 'agregar_empleado.html', {
        'trabajador_form': trabajador_form,
        'contacto_formset': contacto_formset,
        'carga_familiar_formset': carga_familiar_formset,
    })

@user_passes_test(is_admin)
@login_required
def listar_trabajadores(request):
    trabajadores = Trabajador.objects.all()
    return render(request, 'listar_trabajadores.html', {'trabajadores': trabajadores})

@login_required
def home(request):
    trabajador = request.user.trabajador  # Relación OneToOne entre User y Trabajador
    return render(request, 'home.html', {
        'nombre_empleado': trabajador.nombre,
        'cargo': trabajador.cargo,
    })

###DESACTUZALIZADO VVV

@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro creado exitosamente.')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})

@login_required
def book_update(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro actualizado exitosamente.')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})

@login_required
def book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Libro eliminado exitosamente.')
        return redirect('book_list')
    return render(request, 'book_delete.html', {'book': book})

@login_required
def review_create(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    review = Review.objects.filter(book=book, user=request.user).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'Reseña guardada con éxito.')
            return redirect('book_list')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'review_form.html', {'form': form, 'book': book})

@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Reseña eliminada con éxito.')
        return redirect('book_list')
    return render(request, 'review_confirm_delete.html', {'review': review})
