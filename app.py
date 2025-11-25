from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import wikipedia
import socket
import os
import random

app = Flask(__name__)

# Função para checar internet
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Função para gerar respostas estilo ChatGPT
def simulate_chat_response(msg):
    msg_lower = msg.lower()

    # Informações sobre o criador
    if "quem criou" in msg_lower or "criador" in msg_lower:
        return ("Foi criado por António Zacarias Manuel em 25/11/2025. "
                "Mais detalhes: António Zacarias Manuel, telefone 948404462, "
                "email azmanuel@gmail.com, filho de Domingos António Manuel e Jany Paulo Manuel, 17 anos de idade.")

    # Perguntas sobre você
    if "idade" in msg_lower or "quantos anos" in msg_lower:
        return "Tenho 17 anos de idade."

    if "telefone" in msg_lower:
        return "Meu número de contato é 948404462."

    if "email" in msg_lower or "e-mail" in msg_lower:
        return "Meu email é azmanuel@gmail.com."

    # Respostas para perguntas gerais simulando ChatGPT
    general_responses = [
        "Interessante! Pode me dizer mais sobre isso?",
        "Humm, vou tentar explicar: ",
        "Vou responder da melhor forma que posso: ",
        "Deixe-me te contar o que sei: "
    ]
    if any(keyword in msg_lower for keyword in ["quem", "o que", "como", "onde", "quando", "por que"]):
        # Tenta buscar no Wikipedia
        if check_internet():
            try:
                summary = wikipedia.summary(msg, sentences=2, auto_suggest=True, redirect=True)
                return f"{random.choice(general_responses)} {summary}"
            except wikipedia.exceptions.DisambiguationError as e:
                return f"Existem várias opções para '{msg}': {e.options[:5]}"
            except wikipedia.exceptions.PageError:
                return f"Desculpe, não encontrei informações sobre '{msg}'."
            except Exception:
                return "Ocorreu um erro ao buscar informações na internet."
        else:
            return "Estou offline. Por favor, ligue a internet e tente novamente."

    # Resposta padrão
    return "Desculpe, não sei sobre isso. Pergunte algo mais específico ou relacionado a mim."

# Endpoint Twilio
@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.values.get('Body', '')
    response = MessagingResponse()
    reply = simulate_chat_response(incoming_msg)
    response.message(reply)
    return str(response)

# Executa app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
