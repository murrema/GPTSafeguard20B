from flask import Flask, request, jsonify
import requests
import os
import sys
import traceback

app = Flask(__name__)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL", "openai/gpt-oss-safeguard-20b")

@app.route("/", methods=["GET"])
def home():
    return "🔥 GPTSafeguard20B está ativo e aguardando requisições Alexa."

@app.route("/", methods=["POST"])
def alexa_handler():
    try:
        data = request.get_json(force=True, silent=True)
        print("\n📩 Requisição recebida da Alexa:", file=sys.stdout)
        print(data, file=sys.stdout)

        if not data or "request" not in data:
            print("❌ Corpo vazio ou inválido.", file=sys.stdout)
            return gerar_resposta("Erro: corpo da requisição inválido.")

        tipo = data["request"].get("type", "")
        if tipo == "LaunchRequest":
            return gerar_resposta("Modo Insano ativado! O que deseja saber?")
        elif tipo == "IntentRequest":
            intent = data["request"]["intent"]["name"]
            print(f"🎯 Intent detectado: {intent}", file=sys.stdout)
            return gerar_resposta(f"Intent {intent} recebida com sucesso!")
        else:
            return gerar_resposta("Tipo de requisição desconhecido.")

    except Exception as e:
        print("❌ ERRO:", str(e), file=sys.stdout)
        traceback.print_exc()
        return gerar_resposta("Ocorreu um problema interno, tente novamente.")

def gerar_resposta(texto):
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": texto
            },
            "shouldEndSession": False
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
