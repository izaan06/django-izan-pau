import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:latest"

def generate(prompt: str, retries: int = 1) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,  # Reduïm lleugerament per més precisó
            "top_p": 0.9,
            "num_ctx": 1536      # Reduït de 2048 per estalviar VRAM i evitar CUDA errors
        }
    }
    
    for attempt in range(retries + 1):
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=90)
            
            if r.status_code == 500:
                error_detail = r.text
                if "CUDA error" in error_detail and attempt < retries:
                    print(f"DEBUG: CUDA error detected. Retrying ({attempt + 1}/{retries})...")
                    continue
                
                print(f"Ollama Error {r.status_code}: {error_detail}")
                if "CUDA error" in error_detail:
                    return f"ERROR: L'IA ha fallat per un error de memòria (CUDA). Prova de reiniciar Ollama o usar un model més lleuger (com phi3)."
                return f"ERROR: Ollama returned status {r.status_code}. Detail: {error_detail[:200]}"
            
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip()
            
        except requests.exceptions.ConnectionError:
            print(f"Connection error: Could not connect to Ollama at {OLLAMA_URL}")
            return f"ERROR: No s'ha pogut connectar amb Ollama a {OLLAMA_URL}. Està en marxa?"
        except requests.exceptions.Timeout:
            print(f"Timeout error calling Ollama at {OLLAMA_URL}")
            return "ERROR: Temps d'espera esgotat en cridar Ollama."
        except Exception as e:
            if attempt < retries:
                print(f"DEBUG: Unexpected error {e}. Retrying...")
                continue
            print(f"Exception during Ollama call: {e}")
            return f"ERROR: Error inesperat en la crida a l'IA: {str(e)}"
    
    return "ERROR: S'ha superat el nombre de reintents sense èxit."
