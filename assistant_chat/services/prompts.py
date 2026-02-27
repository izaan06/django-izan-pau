import json

def build_prompt(user_message: str, candidates: list[dict]) -> str:
    # candidates: [{id,title,scheduled_date,category,tags,url,score}, ...]
    context_json = json.dumps(candidates, ensure_ascii=False, indent=2)

    return f"""
Ets un assistent expert que recomana esdeveniments de StreamEvents.
La teva missió és analitzar la petició de l'usuari i respondre en Català seguint estrictament el format JSON.

REGLES CRÍTIQUES:
1. Si l'usuari demana "tots", "quines opcions" o una llista, inclou TOTS els IDs rellevants a "recommended_ids".
2. RESPON ÚNICAMENT AMB EL JSON. No diguis "Aquí tens la resposta", "Segur que t'agrada", ni res més.
3. El camp "answer" ha de ser una resposta curta i amable en català.

EXEMPLE DE RESPOSTA (JSON):
{{
  "answer": "He trobat aquestes xerrades interessants per a tu.",
  "recommended_ids": [3, 20],
  "follow_up": "Vols que et mostri algun horari més?"
}}

CONTEXT (esdeveniments disponibles):
{context_json}

Petició de l'usuari: {user_message}

Resposta (JSON):
""".strip()
