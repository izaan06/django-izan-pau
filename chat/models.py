from django.db import models
from django.conf import settings
from django.utils.timesince import timesince

User = settings.AUTH_USER_MODEL

class ChatMessage(models.Model):
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='messages'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_highlighted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"

    def can_delete(self, user):
        if not user.is_authenticated:
            return False
        return (
            user == self.user or
            user == self.event.creator or
            user.is_staff
        )

    def get_user_display_name(self):
        return getattr(self.user, 'display_name', '') or self.user.username

    def get_time_since(self):
        return f"fa {timesince(self.created_at)}"

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Missatge de Xat'
        verbose_name_plural = 'Missatges de Xat'
