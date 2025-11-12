from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Pega variáveis de ambiente
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL", "openai/gpt-oss-safeguard-20b")

@app.route("/", methods=["GET"])
def home():
    return "🔥 GPTSafeguard20B ativo e pronto para a Alexa."

@app.route("/", methods=["POST"])
def alexa_skill():
    try:
        data = request.get_json()
        print("📩 Requisição recebida da Alexa:")
        print(data)

        # Identifica o tipo de requisição
        req_type = data.get("request", {}).get("type", "")
        if req_type == "LaunchRequest":
            response_text = "Modo Insano ativado! O que deseja saber?"
        elif req_type == "IntentRequest":
            intent_name = data["request"]["intent"]["name"]
            query = data["request"]["intent"]["slots"].get("query", {}).get("value", "")
            if not query:
                response_text = f"Você pediu o intent {intent_name}, mas sem uma pergunta."
            else:
                response_text = chamar_openrouter(query)
        else:
            response_text = "Não entendi o tipo de requisição."

        return jsonify(
            {
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": response_text
                    },
                    "shouldEndSession": False
                }
            }
        )

    except Exception as e:
        print(f"❌ Erro interno: {str(e)}")
        return jsonify(
            {
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Houve um problema interno no servidor. Tente novamente."
                    },
                    "shouldEndSession": True
                }
            }
        )

def chamar_openrouter(pergunta):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai/",
            "X-Title": "GPTSafeguard20B"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Você é o modo insano, direto e poderoso."},
                {"role": "user", "content": pergunta}
            ]
        }

        print(f"🚀 Enviando para OpenRouter: {payload}")

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        print("🔁 Status da resposta:", response.status_code)
        print("📦 Corpo:", response.text)

        if response.status_code == 200:
            resposta = response.json()["choices"][0]["message"]["content"]
            return resposta
        else:
            return f"Erro na OpenRouter: {response.status_code}"

    except Exception as e:
        return f"Erro ao conectar ao OpenRouter: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
