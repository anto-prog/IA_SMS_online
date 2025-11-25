from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import random
import json
import os
import urllib.parse
from bs4 import BeautifulSoup

app = Flask(__name__)

# Informações do criador
CRIADOR_INFO = (
    "Foi criado por António Zacarias Manuel. "
    "Mais detalhes: António Zacarias Manuel, número 948404462, "
    "gmail: azmanuel@gmail.com, filho de Domingos António Manuel e Jany Paulo Manuel, "
    "tem 17 anos de idade."
)

# Arquivo local para respostas personalizadas
RESPOSTAS_FILE = "respostas_personalizadas.json"

if os.path.exists(RESPOSTAS_FILE):
    with open(RESPOSTAS_FILE, "r", encoding="utf-8") as f:
        respostas_personalizadas = json.load(f)
else:
    respostas_personalizadas = {}

# Respostas fixas gerais
respostas_fixas = {
    "oi": ["Oi! Estou bem, e você?", "Olá! Que bom falar com você!", "Oi! Como vai?"],
    "tudo bem": ["Tudo ótimo! E você?", "Estou bem, obrigado!", "Tudo certo por aqui!"],
    "quem te criou": [CRIADOR_INFO],
    "empresa": [
        "Nossa empresa é especializada em tecnologia e suporte ao cliente.",
        "Somos uma empresa focada em soluções digitais.",
        "Trabalhamos com inovação e serviços para facilitar a vida dos clientes."
    ]
}

# Função para buscar respostas na web
def busca_web(pergunta):
    try:
        # Primeiro tenta DuckDuckGo
        query = urllib.parse.quote(pergunta)
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&skip_disambig=1&kl=pt-pt"
        resp = requests.get(url, timeout=5).json()
        abstract = resp.get("AbstractText", "")
        if abstract:
            return abstract + " (via DuckDuckGo)"
        # Se não encontrar, faz scraping do Google
        search_url = f"https://www.google.com/search?q={query}&hl=pt"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        snippet = soup.find("div", class_="BNeawe s3v9rd AP7Wnd")
        if snippet:
            return snippet.get_text() + " (via Google)"
        return None
    except requests.exceptions.RequestException:
        return None

def salvar_resposta(pergunta, resposta):
    respostas_personalizadas[pergunta] = resposta
    with open(RESPOSTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(respostas_personalizadas, f, ensure_ascii=False, indent=2)

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body").strip().lower()
    resp = MessagingResponse()
    resposta_enviada = None

    # 1️⃣ Checa respostas personalizadas locais
    if incoming_msg in respostas_personalizadas:
        resposta_enviada = respostas_personalizadas[incoming_msg]

    # 2️⃣ Checa respostas fixas
    if not resposta_enviada:
        for chave in respostas_fixas:
            if chave in incoming_msg:
                resposta_enviada = random.choice(respostas_fixas[chave])
                break

    # 3️⃣ Busca online
    if not resposta_enviada:
        online_resposta = busca_web(incoming_msg)
        if online_resposta:
            resposta_enviada = online_resposta
        else:
            resposta_enviada = "Ops! Estou offline ou não consegui encontrar informações. Conecte à internet."

    resp.message(resposta_enviada)
    return str(resp)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render fornece a porta aqui
    app.run(host="0.0.0.0", port=port)


