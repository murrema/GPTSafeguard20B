from flask import Flask, request, jsonify
import os, requests, html, logging

app = Flask(__name__)

# === CONFIGURAÇÃO DA SUA CHAVE ===
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL", "openai/gpt-oss-safeguard-20b")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gptsafeguard20b")

# === ROTA GET (Render Health Check) ===
@app.route("/", methods=["GET"])
def home():
    return "🔥 GPTSafeguard20B ativo e pronto para a Alexa."

# === ROTA POST (Alexa -> Flask -> OpenRouter) ===
@app.route("/", methods=["POST"])
def alexa_handler():
    try:
        req = request.get_json(force=True)
        logger.info(f"Requisição recebida: {req}")

        # Captura o que o usuário disse
        intent = req.get("request", {}).get("intent", {})
        slots = intent.get("slots", {})
        user_input = ""

        if "query" in slots and slots["query"].get("value"):
            user_input = slots["query"]["value"]
        else:
            for s in slots.values():
                if s.get("value"):
                    user_input = s["value"]
                    break

        if not user_input:
            return alexa_say("Desculpe, não entendi. Pode repetir sua pergunta?")

        # Envia a pergunta pro modelo da OpenRouter
        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Você é o GPT Safeguard 20B — uma IA avançada, "
                        "adaptativa, detalhada e natural. Responda sempre em português do Brasil, "
                        "com clareza e empatia. Seja preciso e explique se necessário."
                    )
                },
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 600,
            "temperature": 0.8
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "GPTSafeguard20B"
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=payload, timeout=30
        )
        data = response.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        if not reply:
            reply = "O modelo não respondeu agora. Pode tentar novamente."

        return alexa_say(reply)

    except Exception as e:
        logger.exception("Erro geral no servidor:")
        return alexa_say(f"Ocorreu um erro interno: {e}")

# === Formata resposta para Alexa ===
def alexa_say(text, end_session=False):
    text = html.escape(text)
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end_session
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
