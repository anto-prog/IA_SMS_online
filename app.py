from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import wikipedia
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Configuração do Wikipedia para evitar warnings
wikipedia.set_lang("pt")  # ou "en" se preferir inglês

@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body', '').strip()
    resp = MessagingResponse()
    
    # Verifica se há internet
    try:
        # Resposta padrão para perguntas pessoais
        if "quem te criou" in incoming_msg.lower():
            resposta = (
                "Fui criado por António Zacarias Manuel. "
                "Mais detalhes: telefone 948404462, email azmanuel@gmail.com, "
                "filho de Domingos António Manuel e Jany Paulo Manuel, 17 anos."
            )
            resp.message(resposta)
        
        # Resposta padrão simples
        elif incoming_msg.lower() in ["oi", "olá", "ola"]:
            resp.message("Oi! Estou bem e você?")
        
        # Busca na Wikipedia
        else:
            try:
                resultado = wikipedia.summary(incoming_msg, sentences=2)
                # Limpeza do HTML
                clean_result = BeautifulSoup(resultado, features="html.parser").text
                resp.message(clean_result)
            except wikipedia.exceptions.DisambiguationError as e:
                resp.message(f"Existe mais de uma opção para '{incoming_msg}'. Tente ser mais específico.")
            except wikipedia.exceptions.PageError:
                resp.message("Desculpe, não encontrei informações sobre isso.")
    
    except Exception as e:
        resp.message("Parece que não estou conectado à internet ou ocorreu um erro. Por favor, verifique a conexão.")
    
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)