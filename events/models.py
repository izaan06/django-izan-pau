from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
import urllib.parse


User = get_user_model()  # Obté el model d'usuari personalitzat


class Event(models.Model):
    # Choices per categories d'esdeveniments
    CATEGORY_CHOICES = [
        ('gaming', 'Gaming'),
        ('music', 'Música'),
        ('talk', 'Xerrades'),
        ('education', 'Educació'),
        ('sports', 'Esports'),
        ('entertainment', 'Entreteniment'),
        ('technology', 'Tecnologia'),
        ('art', 'Art i Creativitat'),
        ('other', 'Altres'),
    ]

    # Choices per estats dels esdeveniments
    STATUS_CHOICES = [
        ('scheduled', 'Programat'),
        ('live', 'En Directe'),
        ('finished', 'Finalitzat'),
        ('cancelled', 'Cancel·lat'),
    ]

    # Camps del model
    title = models.CharField(max_length=200)  # Títol
    description = models.TextField()           # Descripció
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuari creador
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # Categoria
    scheduled_date = models.DateTimeField()    # Data i hora programada
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')  # Estat
    thumbnail = models.ImageField(upload_to='events/thumbnails/', blank=True, null=True)  # Imatge portada
    max_viewers = models.PositiveIntegerField(default=100)  # Màxim espectadors
    is_featured = models.BooleanField(default=False)  # Esdeveniment destacat
    created_at = models.DateTimeField(auto_now_add=True)  # Data creació automàtica
    updated_at = models.DateTimeField(auto_now=True)      # Última actualització automàtica
    tags = models.CharField(max_length=500, blank=True)   # Etiquetes separades per comes
    stream_url = models.URLField(max_length=500, blank=True)  # URL de streaming/demo

    # Duracions per categoria (en minuts)
    category_durations = {
        'gaming': 180,
        'music': 90,
        'talk': 60,
        'education': 120,
        'sports': 150,
        'entertainment': 120,
        'technology': 90,
        'art': 120,
        'other': 90,
    }
    
    # Thumbnails per defecte per categoria
    DEFAULT_THUMBNAILS = {
        'gaming': 'events/defaults/gaming.jpeg',
        'music': 'events/defaults/music.jpeg',
        'talk': 'events/defaults/talk.jpg',
        'education': 'events/defaults/education.jpg',
        'sports': 'events/defaults/sports.jpeg',
        'entertainment': 'events/defaults/entertainment.jpeg',
        'technology': 'events/defaults/technology.jpg',
        'art': 'events/defaults/art.jpg',
        'other': 'events/defaults/other.jpg',
    }

    DEFAULT_IMAGE = 'events/defaults/default.jpg'  # Imatge genèrica per defecte

    @property
    def thumbnail_or_default(self):
        """
        Retorna la imatge del thumbnail si existeix,
        sinó retorna una imatge per categoria o la genèrica.
        """
        if self.thumbnail:
            return self.thumbnail.url
        path = self.DEFAULT_THUMBNAILS.get(self.category, self.DEFAULT_IMAGE)
        return settings.MEDIA_URL + path

    # Representació en string del model (per admin i debugging)
    def __str__(self):
        return self.title

    # URL de detall de l'esdeveniment
    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})

    # Propietats per l'estat de l'esdeveniment
    @property
    def is_live(self):
        return self.status == 'live'

    @property
    def is_upcoming(self):
        return self.scheduled_date > timezone.now() and self.status == 'scheduled'

    # Durada de l’esdeveniment si està finalitzat
    def get_duration(self):
        if self.status == 'finished':
            minutes = self.category_durations.get(self.category, 90)
            return timedelta(minutes=minutes)
        return None

    # Llista d’etiquetes separades per comes
    @property
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    # Conversió de l'URL de streaming a format embed per YouTube/Twitch
    def get_stream_embed_url(self):
        if not self.stream_url:
            return None

        # YouTube
        if "youtube.com" in self.stream_url or "youtu.be" in self.stream_url:
            parsed_url = urllib.parse.urlparse(self.stream_url)
            video_id = None

            # youtu.be/<id>
            if "youtu.be" in self.stream_url:
                video_id = parsed_url.path.lstrip('/')

            # watch?v=<id>
            if not video_id:
                query = urllib.parse.parse_qs(parsed_url.query)
                video_id = query.get("v", [None])[0]

            # shorts
            if not video_id and "/shorts/" in parsed_url.path:
                video_id = parsed_url.path.split("/shorts/")[1]

            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?rel=0&autoplay=0"

        # Twitch
        if "twitch.tv" in self.stream_url:
            username = self.stream_url.rstrip('/').split("/")[-1]
            return f"https://player.twitch.tv/?channel={username}&parent=127.0.0.1"

        # Si no és YouTube/Twitch, retorna la URL original
        return self.stream_url

    class Meta:
        ordering = ['-created_at']  # Els més recents primer
        verbose_name = 'Esdeveniment'
        verbose_name_plural = 'Esdeveniments'
