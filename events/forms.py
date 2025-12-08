from django import forms
from .models import Event
from django.utils import timezone

# Formulari per crear un esdeveniment
class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event  # Model vinculat al formulari
        fields = ['title', 'description', 'category', 'scheduled_date', 'thumbnail', 'max_viewers', 'tags', 'stream_url']
        widgets = {
            # Widget per seleccionar data i hora amb HTML5
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            # Textarea amb classes de Bootstrap per a la descripció
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            # Input de fitxer per pujar la imatge de portada
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # Validació de la data programada: no pot ser en el passat
    def clean_scheduled_date(self):
        date = self.cleaned_data['scheduled_date']
        if date < timezone.now():
            raise forms.ValidationError("La data no pot ser en el passat.")
        return date

    # Validació del nombre màxim d'espectadors (1-1000)
    def clean_max_viewers(self):
        viewers = self.cleaned_data['max_viewers']
        if not (1 <= viewers <= 1000):
            raise forms.ValidationError("El número màxim d'espectadors ha d'estar entre 1 i 1000.")
        return viewers


# Formulari per actualitzar un esdeveniment existent
class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        # Inclou també l'estat de l'esdeveniment
        fields = ['title', 'description', 'category', 'scheduled_date', 'thumbnail', 'max_viewers', 'tags', 'status', 'stream_url']
        widgets = EventCreationForm.Meta.widgets  # Reutilitza els widgets del formulari de creació

    # No es pot canviar la data si l'esdeveniment està en directe
    def clean_scheduled_date(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.is_live:  # is_live és una propietat del model
            raise forms.ValidationError("No es pot canviar la data d’un esdeveniment en directe.")
        return self.cleaned_data['scheduled_date']


# Formulari de cerca i filtres per llistat d'esdeveniments
class EventSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Cerca',
        widget=forms.TextInput(attrs={'class': 'form-control'})  # Input de text amb classe Bootstrap
    )
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'Totes')] + Event.CATEGORY_CHOICES,  # Inclou opció "Totes"
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Tots')] + Event.STATUS_CHOICES,  # Inclou opció "Tots"
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})  # Selector de data HTML5
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})  # Selector de data HTML5
    )
