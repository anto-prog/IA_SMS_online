from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import wikipedia
import requests
import socket
import os

app = Flask(__name__)

# Função para checar internet
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Função para processar mensagens
def process_message(msg):
    msg_lower = msg.lower()

    # Quem criou
    if "quem criou" in msg_lower:
        return ("Foi criado por António Zacarias Manuel "
                "em 25/11/2025. "
                "Mais detalhes: António Zacarias Manuel, "
                "telefone 948404462, email azmanuel@gmail.com, "
                "filho de Domingos António Manuel e Jany Paulo Manuel, 17 anos de idade.")

    # Mensagem geral sobre internet
    if not check_internet():
        return "Estou offline. Por favor, ligue a internet e tente novamente."

    # Busca no Wikipedia
    try:
        summary = wikipedia.summary(msg, sentences=2, auto_suggest=True, redirect=True)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Existem várias opções para '{msg}': {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        # Se não encontrar no Wikipedia, responde algo genérico
        return f"Desculpe, não encontrei informações sobre '{msg}'."
    except Exception:
        return "Ocorreu um erro ao buscar informações."

# Endpoint para Twilio (SMS ou WhatsApp)
@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.values.get('Body', '')
    response = MessagingResponse()
    reply = process_message(incoming_msg)
    response.message(reply)
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Para Render
    app.run(host="0.0.0.0", port=port)
