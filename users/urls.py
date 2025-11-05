from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # Registro de un usuario nuevo
    path("register/", views.register_view, name="register"),

    # Inicio de sesión
    path("login/", views.login_view, name="login"),

    # Cierre de sesión
    path("logout/", views.logout_view, name="logout"),

    # Perfil del usuario autenticado
    path("profile/", views.profile_view, name="profile"),

    # Editar perfil
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),

    # Perfil público (por username)
    path("user/<str:username>/", views.public_profile_view, name="public_profile"),
]
