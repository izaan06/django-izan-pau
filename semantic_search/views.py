from django.shortcuts import render
from django.utils import timezone
from django.db import models

from events.models import Event
from .services.embeddings import embed_text, model_name
from .services.ranker import cosine_top_k

def _event_text(e: Event) -> str:
    parts = [
        e.title or "",
        e.description or "",
        e.category or "",
        e.tags or "",
    ]
    return " | ".join([p.strip() for p in parts if p and p.strip()])

def semantic_search(request):
    q = (request.GET.get("q") or "").strip()
    only_future = request.GET.get("only_future") == "1"

    results = []
    if q:
        q_vec = embed_text(q)

        qs = Event.objects.all()
        if only_future:
            # Filtrem per esdeveniments programats O futurs
            qs = qs.filter(models.Q(scheduled_date__gte=timezone.now()) | models.Q(status='scheduled'))

        # Carreguem candidats i fem ranking en Python
        items = []
        for e in qs:
            # Si no té embedding, no el podem rankejar
            items.append((e, getattr(e, "embedding", None)))

        ranked = cosine_top_k(q_vec, items, k=20)
        results = [
            {'event': e, 'score': s, 'score_pct': min(100, max(0, int(s * 100)))}
            for e, s in ranked
        ]

    context = {
        "query": q,
        "results": results,  # llista de tuples (Event, score)
        "only_future": only_future,
        "embedding_model": model_name(),
    }
    return render(request, "semantic_search/search.html", context)
