import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assistant_chat.services.retriever import retrieve_events

query = "diguem esdeveniments futurs"
# Simulem el que fa la vista
ranked = retrieve_events(query, only_future=True, k=10)

print(f"Results for query: '{query}'")
for e, score in ranked:
    print(f"ID:{e.pk} | Score:{score:.4f} | Title:{e.title} | Cat:{e.category}")
