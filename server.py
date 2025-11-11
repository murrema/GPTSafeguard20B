# server.py — Alexa + OpenRouter (GPT Safeguard 20B)
from flask import Flask, request, jsonify
import requests, os, html, logging, random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gptsafeguard")

# === CONFIGURAÇÃO DA SUA CHAVE ===
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-SEU_TOKEN_AQUI")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-safeguard-20b"


# ===============================
# 🔹 ROTA GET (Render Health Check)
# ===============================
@app.route("/", methods=["GET"])
def home():
    return "🔥 GPTSafeguard20B ativo e pronto para a Alexa."


# ===============================
# 🔹 ROTA POST (Alexa → Flask → OpenRouter)
# ===============================
@app.route("/", methods=["POST"])
def alexa_handler():
    try:
        req = request.get_json(force=True)
        logger.info("📩 Requisição Alexa: %s", req.get("request", {}).get("type"))

        # 1️⃣ Quando o usuário só diz “abrir modo insano”
        if req.get("request", {}).get("type") == "LaunchRequest":
            return alexa_say("🔥 Modo Insano ativado! Eu sou o GPT Safeguard 20B. Pode perguntar o que quiser!")

        # 2️⃣ Quando o usuário fala algo (IntentRequest)
        if req.get("request", {}).get("type") == "IntentRequest":
            intent = req["request"]["intent"]
            slots = intent.get("slots", {})
            user_input = ""

            # Captura o texto dito pelo usuário
            if "query" in slots and slots["query"].get("value"):
                user_input = slots["query"]["value"]
            else:
                for s in slots.values():
                    if s.get("value"):
                        user_input = s["value"]
                        break

            if not user_input:
                return alexa_say("Desculpe, não entendi. Pode repetir sua pergunta?")

            # Monta o prompt pro OpenRouter
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": (
                        "Você é o GPT Safeguard 20B — uma IA com inteligência e emoção humanas, "
                        "capaz de dar respostas claras, detalhadas e empáticas. "
                        "Adapte o tom entre sério e descontraído conforme a situação."
                    )},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 500,
                "temperature": 0.9
            }

            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "HTTP-Referer": "https://openrouter.ai/",
                "X-Title": "GPTSafeguard20B",
                "Content-Type": "application/json"
            }

            # Envia pro modelo
            try:
                response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
                data = response.json()
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not reply:
                    reply = "Desculpe, o modelo não respondeu agora."
            except Exception as e:
                reply = f"Ocorreu um erro de conexão com o modelo: {e}"

            # Retorna pra Alexa falar
            return alexa_say(reply)

        # 3️⃣ Se for outro tipo de requisição
        return alexa_say("Desculpe, não entendi o tipo de requisição.")

    except Exception as e:
        logger.exception("Erro geral no servidor:")
        return alexa_say(f"Ocorreu um erro interno: {e}")


# ===============================
# 🔹 Função pra formatar resposta da Alexa
# ===============================
def alexa_say(text, end_session=False):
    text = html.escape(text)
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end_session
        }
    })


# ===============================
# 🔹 Executar servidor
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
