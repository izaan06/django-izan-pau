# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings

from .forms import CustomUserCreationForm, CustomUserUpdateForm, CustomAuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


def register_view(request):
    """
    GET: mostrar formulari
    POST: processar registre amb CustomUserCreationForm
    -> login automàtic i redirecció a perfil (users:profile)
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  
            messages.success(request, "Registre correcte. Benvingut/da!")
            return redirect(reverse("users:profile"))
        else:
            messages.error(request, "Si us plau, corregeix els errors del formulari.")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    """
    Vista de login utilitzant CustomAuthenticationForm.
    Si POST i form vàlid -> auth_login i redirigeix.
    """
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Benvingut/da, {user.get_short_name() or user.username}!")
            # redirigir a next si existeix
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return HttpResponseRedirect(next_url)
            return redirect(reverse("users:profile"))
        else:
            messages.error(request, "Nom d'usuari/email o contrasenya incorrectes.")
    else:
        form = CustomAuthenticationForm(request)
    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    """
    Tanca la sessió i redirigeix a la pàgina principal
    """
    auth_logout(request)
    messages.info(request, "Has tancat sessió.")
    # Ajusta la URL de la pàgina principal segons el teu projecte
    return redirect("/")


@login_required
def profile_view(request):
    """
    Mostra el perfil de l'usuari autenticat.
    """
    user = request.user
    return render(request, "users/profile.html", {"user": user})


@login_required
def edit_profile_view(request):
    """
    Permet l'edició del perfil amb CustomUserUpdateForm.
    Gestiona pujada d'avatar via request.FILES.
    """
    user = request.user
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualitzat correctament.")
            return redirect(reverse("users:profile"))
        else:
            messages.error(request, "Si us plau, corregeix els errors del formulari.")
    else:
        form = CustomUserUpdateForm(instance=user)
    return render(request, "users/edit_profile.html", {"form": form})


def public_profile_view(request, username):
    """
    Mostra el perfil públic d'un altre usuari.
    Si no existeix -> 404.
    """
    other_user = get_object_or_404(User, username=username)
    return render(request, "users/public_profile.html", {"user_obj": other_user})
