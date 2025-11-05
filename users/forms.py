# users/forms.py
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re

User = get_user_model()

USERNAME_REGEX = re.compile(r'^[\w.@+-]+$')  # lletres, números i @/./+/-/_

class CustomUserCreationForm(forms.ModelForm):
    """
    Formulari per crear un usuari:
    - Base ModelForm (per fer servir el model custom)
    - password1 i password2 definides manualment i validades amb validate_password
    - email ha de ser únic
    - username amb format vàlid
    """
    password1 = forms.CharField(
        label="Contrasenya",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Introdueix una contrasenya segura."
    )
    password2 = forms.CharField(
        label="Confirmar contrasenya",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = User.objects.filter(email__iexact=email)
            if qs.exists():
                raise ValidationError("Ja existeix un usuari amb aquest email.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and not USERNAME_REGEX.match(username):
            raise ValidationError(
                "El nom d'usuari només pot contenir lletres, números i els símbols @/./+/-/_"
            )
        return username

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if not p1 or not p2:
            raise ValidationError("Ambdues contrasenyes són obligatòries.")
        if p1 != p2:
            raise ValidationError("Les contrasenyes no coincideixen.")
        try:
            validate_password(p1, user=None)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password1"]
        user.set_password(password)
        if commit:
            user.save()
        return user


class CustomUserUpdateForm(forms.ModelForm):
    """
    Formulari per editar el perfil de l'usuari.
    Inclou widgets per a bio (Textarea) i avatar (FileInput).
    """
    class Meta:
        model = User
        fields = ("first_name", "last_name", "display_name", "bio", "avatar")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Escriu alguna cosa sobre tu..."}),
            "avatar": forms.FileInput(),
        }


class CustomAuthenticationForm(AuthenticationForm):
    """
    Permet iniciar sessió amb username o email.
    Hereta AuthenticationForm per aprofitar la gestió d'autenticació.
    Si l'usuari introdueix un email, es busca l'username associat (assumim email únic).
    """
    username = forms.CharField(label="Usuari o email")

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            # Si té @ -> potencialment email; també acceptem username amb @ si el model ho permet,
            # així que comprovem primer si existeix usuari amb aquest username exactament.
            user_candidate = None
            # 1) intentem per username exacte
            try:
                user_candidate = User.objects.get(username__iexact=username_or_email)
            except User.DoesNotExist:
                # 2) intentem per email
                try:
                    user_candidate = User.objects.get(email__iexact=username_or_email)
                except User.DoesNotExist:
                    user_candidate = None

            if user_candidate:
                username_lookup = user_candidate.get_username()
            else:
                username_lookup = username_or_email  # fallback, AuthenticationForm gestionarà l'error

            # cridem authenticate
            self.user_cache = authenticate(self.request, username=username_lookup, password=password)
            if self.user_cache is None:
                raise ValidationError(self.error_messages['invalid_login'], code='invalid_login')
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
