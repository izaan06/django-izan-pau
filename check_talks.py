import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.models import Event
talks = Event.objects.filter(category='talk')
print(f"Total talks: {talks.count()}")
for t in talks:
    print(f"- {t.title} (ID: {t.pk}, Status: {t.status}, Date: {t.scheduled_date})")
