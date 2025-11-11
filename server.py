from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Usa a chave da API do Render (configurada nas variáveis de ambiente)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "🔥 GPT Safeguard 20B está online e pronto para agir. 🔥"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        query = data.get("query", "")
        history = data.get("history", [])

        if not query:
            return jsonify({"error": "Nenhuma entrada recebida."}), 400

        # Montagem do contexto inteligente com memória curta
        messages = [{"role": "system", "content": (
            "Você é o GPT Safeguard 20B, uma IA altamente inteligente, precisa, "
            "adaptativa e equilibrada. Responda como uma versão superior, "
            "usando linguagem natural e raciocínio de alto nível. "
            "Alterne entre respostas curtas e longas conforme o contexto exige. "
            "Sempre mantenha tom humano, empático e envolvente."
        )}]

        for msg in history[-6:]:  # mantém as últimas interações
            messages.append({"role": "user", "content": msg})

        messages.append({"role": "user", "content": query})

        # Chamada para o modelo principal
        completion = openai.ChatCompletion.create(
            model="openai/gpt-oss-safeguard-20b",
            messages=messages,
            max_tokens=500,
            temperature=0.9,
        )

        reply = completion.choices[0].message["content"]
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
