import os
import html
import logging
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gpt-alexa")

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-safeguard-20b"

def alexa_say(text, should_end_session=True):
    ssml = f"<speak>{html.escape(text)}</speak>"
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "SSML", "ssml": ssml},
            "shouldEndSession": should_end_session
        },
        "sessionAttributes": {}
    })

@app.route("/", methods=["GET"])
def home():
    return "OK - GPT Safeguard 20B online", 200

@app.route("/alexa", methods=["POST"])
def alexa_handler():
    try:
        data = request.get_json(force=True)
        rtype = data.get("request", {}).get("type")

        if rtype == "LaunchRequest":
            return alexa_say("Modo Insano ativado! Pode perguntar o que quiser.", False)

        if rtype == "IntentRequest":
            intent = data["request"]["intent"]
            query = intent.get("slots", {}).get("query", {}).get("value", "")
            if not query:
                return alexa_say("Desculpe, não entendi sua pergunta.", False)

            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "Você é um assistente inteligente e responde em português."},
                    {"role": "user", "content": query}
                ]
            }

            try:
                r = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=40)
                r.raise_for_status()
                data = r.json()
                reply = data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(e)
                reply = "Erro ao conectar com o modelo OpenRouter."

            return alexa_say(reply, True)

        return alexa_say("Desculpe, algo deu errado.", True)

    except Exception as e:
        logger.exception(e)
        return alexa_say("Erro interno no servidor.", True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
