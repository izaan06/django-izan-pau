import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .services.retriever import retrieve_events
from .services.prompts import build_prompt
from .services.llm_ollama import generate

def chat_page(request):
    return render(request, "assistant_chat/chat.html")

@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message = (payload.get("message") or "").strip()
    only_future = bool(payload.get("only_future", True))

    if not message:
        return JsonResponse({"error": "Empty message"}, status=400)

    ranked = retrieve_events(message, only_future=only_future, k=8)
    print(f"DEBUG: retrieve_events returned {len(ranked)} events")

    # prepara candidats per al context del LLM
    candidates = []
    for e, score in ranked:
        candidates.append({
            "id": int(e.pk),
            "title": e.title,
            "scheduled_date": e.scheduled_date.isoformat() if e.scheduled_date else None,
            "category": e.get_category_display(),
            "tags": e.tags or "",
            "url": e.get_absolute_url(),
            "score": round(float(score), 3),
        })
    print(f"DEBUG: candidates count: {len(candidates)}")

    prompt = build_prompt(message, candidates)
    print(f"Prompt length: {len(prompt)} characters")
    llm_text = generate(prompt)

    # DEBUG
    print(f"--- DEBUG OLLAMA START ---")
    print(f"User Message: {message}")
    print(f"Raw Output: {llm_text}")
    print(f"--- DEBUG OLLAMA END ---")

    # parse JSON resposta del model
    try:
        # Check if generate returned an error message starting with 'ERROR:'
        if llm_text.startswith("ERROR:"):
            raise ValueError(llm_text)

        # Extract JSON from potential explanatory text
        cleaned_text = llm_text.strip()
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_text:
            parts = cleaned_text.split("```")
            if len(parts) >= 3:
                cleaned_text = parts[1].strip()
        
        # Sometimes it might just have { ... } somewhere in the text
        if not (cleaned_text.startswith('{') and cleaned_text.endswith('}')):
            import re
            match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if match:
                cleaned_text = match.group(0)

        llm_json = json.loads(cleaned_text)
    except Exception as e:
        print(f"Parsing error: {e}")
        # fallback segur millorat
        error_msg = str(e)
        if "ERROR:" in error_msg:
             if "CUDA" in error_msg or "memòria" in error_msg:
                 answer = "Sembla que el servidor d'IA té problemes de memòria (GPU). Tot i així, aquí tens els esdeveniments més rellevants:"
             else:
                 answer = f"No s'ha pogut generar una resposta IA: {error_msg}. Tanmateix, he trobat aquests esdeveniments:"
        else:
             answer = "No he pogut estructurar la resposta IA, però aquí tens els esdeveniments més rellevants:"

        llm_json = {
            "answer": answer,
            "recommended_ids": [c["id"] for c in candidates[:6]],
            "follow_up": "Prova de ser més específic o verifica que Ollama estigui funcionant."
        }

    # filtra recommended_ids perquè només siguin dels candidats
    allowed = {c["id"] for c in candidates}
    rec_ids = [i for i in llm_json.get("recommended_ids", []) if i in allowed]

    # prepara cards finals
    cards = [c for c in candidates if c["id"] in rec_ids]
    if not cards and candidates:
        # si el model no n'ha seleccionat cap, agafa top-6
        cards = candidates[:6]

    return JsonResponse({
        "answer": llm_json.get("answer", ""),
        "follow_up": llm_json.get("follow_up", ""),
        "events": cards,
    })
