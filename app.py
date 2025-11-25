from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup
import wikipedia

app = Flask(__name__)

# Configurações básicas
CREATOR_INFO = (
    "Foi criado por António Zacarias Manuel em 25/11/2025. "
    "Detalhes: António Zacarias Manuel, número 948404462, "
    "email azmanuel@gmail.com, filho de Domingos António Manuel e Jany Paulo Manuel, 17 anos."
)

def search_wikipedia(query):
    try:
        wikipedia.set_lang("pt")
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except Exception:
        return None

def search_google(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.google.com/search?q={query}"
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        results = soup.find_all("div", class_="BNeawe s3v9rd AP7Wnd")
        for result in results[:3]:
            return result.get_text()
        return "Não consegui encontrar nada relevante."
    except Exception:
        return "Não consegui acessar a internet. Conecte-se e tente novamente."

@app.route("/sms", methods=['POST'])
def sms_reply():
    msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()

    if not msg:
        resp.message("Recebi uma mensagem vazia. Pode escrever algo para eu responder.")
        return str(resp)

    # Respostas especiais
    if "quem te criou" in msg:
        resp.message(CREATOR_INFO)
        return str(resp)
    elif "oi" in msg or "olá" in msg:
        resp.message("Oi! Estou bem, e você? 😊")
        return str(resp)
    elif "ligar a internet" in msg or "offline" in msg:
        resp.message("Parece que estou offline. Conecte a internet para que eu possa responder corretamente.")
        return str(resp)

    # Tenta buscar no Wikipedia primeiro
    resposta = search_wikipedia(msg)
    if resposta:
        resp.message(resposta)
        return str(resp)

    # Se não encontrar, tenta buscar no Google
    resposta_google = search_google(msg)
    resp.message(resposta_google)
    return str(resp)

if __name__ == "__main__":
    # Render exige bind em 0.0.0.0 e porta de ambiente
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)