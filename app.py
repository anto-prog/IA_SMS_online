from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import wikipedia
import requests

app = Flask(__name__)

# Função principal para processar mensagens
def process_message(message):
    message_lower = message.lower()

    # Respostas sobre o criador
    if "quem te criou" in message_lower:
        return ("Fui criado por António Zacarias Manuel "
                "em 25/11/2025. Detalhes: telefone 948404462, "
                "email azmanuel@gmail.com, filho de Domingos António Manuel e Jany Paulo Manuel, 17 anos de idade.")

    # Resposta genérica sobre Wikipedia
    try:
        if len(message.split()) > 1:
            summary = wikipedia.summary(message, sentences=2, auto_suggest=True)
            return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Existem várias opções para '{message}': {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        pass
    except Exception:
        pass

    # Resposta padrão caso não encontre info
    return "Desculpe, não consegui encontrar informações sobre isso. Pergunta outra coisa!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    # Pega o texto enviado pelo WhatsApp/Twilio
    incoming_msg = request.form.get('Body', '')
    
    if not incoming_msg:
        resp = MessagingResponse()
        resp.message("Erro: não recebi nenhuma mensagem. Por favor, envie texto.")
        return str(resp)

    # Processa a mensagem
    reply_text = process_message(incoming_msg)

    # Cria resposta Twilio
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
