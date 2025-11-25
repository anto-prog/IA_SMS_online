from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import wikipedia
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Configurações do Wikipedia para português
wikipedia.set_lang("pt")

def buscar_internet(pergunta):
    """Busca na Wikipedia; se não encontrar, tenta uma busca no Google."""
    try:
        resultado = wikipedia.summary(pergunta, sentences=2)
        return resultado
    except Exception:
        # Busca no Google usando requests e BeautifulSoup (simples)
        try:
            query = pergunta.replace(" ", "+")
            url = f"https://www.google.com/search?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(resp.text, "lxml")
            snippet = soup.find("div", {"class": "BNeawe s3v9rd AP7Wnd"})
            if snippet:
                return snippet.text
            return "Não consegui encontrar uma resposta online."
        except:
            return "Não consegui acessar a internet."

@app.route("/sms", methods=["POST"])
def sms_reply():
    """Função principal que responde às mensagens WhatsApp/SMS."""
    mensagem = request.form.get("Body", "").strip().lower()
    resp = MessagingResponse()
    
    if not mensagem:
        resp.message("Por favor, envie uma pergunta.")
        return str(resp)
    
    # Respostas personalizadas
    if "quem te criou" in mensagem:
        resp.message(
            "Fui criado por António Zacarias Manuel no dia 25/11/2025. "
            "Mais detalhes: António Zacarias Manuel, telefone: 948404462, "
            "email: azmanuel@gmail.com, filho de Domingos António Manuel e Jany Paulo Manuel, 17 anos."
        )
        return str(resp)
    
    if "ligue a internet" in mensagem or "está offline" in mensagem:
        resp.message("No momento não consigo acessar a internet. Por favor, verifique sua conexão.")
        return str(resp)
    
    # Resposta padrão usando busca
    resposta = buscar_internet(mensagem)
    resp.message(resposta)
    return str(resp)

if __name__ == "__main__":
    # Porta dinâmica para Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

