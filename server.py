# server.py — Alexa <> OpenRouter (GPT Safeguard 20B)
from flask import Flask, request, jsonify
import requests, os, html, logging, random, re

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gptsafeguard")

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-SEU_TOKEN_AQUI")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-safeguard-20b"

# utilitários mínimos
def safe_text(t):
    return html.escape(t or "")

@app.route("/", methods=["POST"])
def alexa_handler():
    req = request.get_json(force=True)
    logger.info("Received Alexa request: %s", req.get("request", {}).get("type"))
    # LaunchRequest
    if req.get("request", {}).get("type") == "LaunchRequest":
        speak = "🔥 Modo Insano ativado! Eu sou o GPT Safeguard 20B. Diga sua pergunta."
        return alexa_ssml_response(speak, session_attrs=req.get("session", {}).get("attributes", {}))
    # IntentRequest
    if req.get("request", {}).get("type") == "IntentRequest":
        intent = req["request"]["intent"]
        # pega slot 'query' com segurança
        user_input = ""
        slots = intent.get("slots", {}) or {}
        if "query" in slots and slots["query"].get("value"):
            user_input = slots["query"]["value"]
        else:
            # tenta pegar qualquer slot disponível
            for s in slots.values():
                if s.get("value"):
                    user_input = s.get("value")
                    break
        if not user_input:
            return alexa_ssml_response("Desculpe, não entendi. Pode repetir?", session_attrs=req.get("session", {}).get("attributes", {}))

        # Monta prompt (sistema + usuário)
        system_msg = {
            "role": "system",
            "content": (
                "Você é o GPT Safeguard 20B — ultra inteligente, detalhado e adaptativo. "
                "Responda em português de forma clara, precisa e natural. Se for pergunta de follow-up, use o contexto."
            )
        }
        messages = [system_msg, {"role":"user","content": user_input}]

        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": 700,
            "temperature": 0.8
        }
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "gptsafeguard-alexa"
        }
        try:
            r = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=25)
            r.raise_for_status()
            data = r.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not reply:
                reply = "Desculpe, não obtive resposta do modelo agora."
        except Exception as e:
            logger.exception("OpenRouter error")
            reply = random.choice([
                "Desculpe, houve um problema de conexão com o modelo. Tente novamente em alguns segundos.",
                "Não consegui acessar o modelo agora. Posso tentar responder de forma simples sem o modelo?"
            ])

        # Retorna como SSML (Alexa)
        return alexa_ssml_response(reply, session_attrs=req.get("session", {}).get("attributes", {}))

    # fallback
    return alexa_ssml_response("Desculpe, não consegui entender a requisição.", should_end=True)

def alexa_ssml_response(text, should_end=False, session_attrs=None):
    ssml = f"<speak>{safe_text(text)}</speak>"
    res = {
        "version": "1.0",
        "sessionAttributes": session_attrs or {},
        "response": {
            "outputSpeech": {"type": "SSML", "ssml": ssml},
            "shouldEndSession": bool(should_end)
        }
    }
    return jsonify(res)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
