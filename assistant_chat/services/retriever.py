from django.utils import timezone
from events.models import Event
from semantic_search.services.embeddings import embed_text
from semantic_search.services.ranker import cosine_top_k

def build_event_text(e: Event) -> str:
    return " | ".join([
        (e.title or "").strip(),
        (e.description or "").strip(),
        (e.category or "").strip(),
        (e.tags or "").strip(),
    ]).strip()

def retrieve_events(query: str, only_future: bool = True, k: int = 8):
    q_vec = embed_text(query)
    if not q_vec:
        return []

    qs = Event.objects.all()
    if only_future:
        qs = qs.filter(scheduled_date__gte=timezone.now())

    items = []
    for e in qs:
        emb = getattr(e, "embedding", None)
        
        # Si no té embedding, el generem "lazy" (en calent)
        if not (isinstance(emb, list) and len(emb) > 0):
            print(f"DEBUG: Generating missing embedding for event {e.pk}: {e.title}")
            text = build_event_text(e)
            emb = embed_text(text)
            if emb:
                e.embedding = emb
                e.save(update_fields=["embedding"])
        
        if isinstance(emb, list) and len(emb) > 0:
            items.append((e, emb))

    ranked = cosine_top_k(q_vec, items, k=max(k, 30))
    print(f"DEBUG: cosine_top_k returned {len(ranked)} items")

    # Llindar mínim per evitar recomanar qualsevol cosa
    ranked = [(e, s) for (e, s) in ranked if s >= 0.20]
    print(f"DEBUG: items above threshold (0.20): {len(ranked)}")

    # retalla a k
    return ranked[:k]
