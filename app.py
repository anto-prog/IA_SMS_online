from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import wikipedia
from googlesearch import search
import re

# Configurações iniciais
wikipedia.set_lang("pt")  # Define o Wikipedia em português

app = Flask(__name__)

# Dados do criador
CRIADOR = {
    "nome": "António Zacarias Manuel",
    "telefone": "948404462",
    "email": "azmanuel@gmail.com",
    "pais": "Angola",
    "pais_pais": "Angola",
    "pais_parentes": "filho de Domingos António Manuel e Jany Paulo Manuel",
    "idade": 17
}

def busca_google(query, max_results=3):
    try:
        resultados = []
        for url in search(query, num_results=max_results):
            resultados.append(url)
        if resultados:
            return "Aqui estão alguns links que podem ajudar:\n" + "\n".join(resultados)
        else:
            return "Desculpe, não encontrei informações relevantes no Google."
    except Exception:
        return "Desculpe, ocorreu um erro ao buscar informações no Google."

def busca_wikipedia(query):
    try:
        resumo = wikipedia.summary(query, sentences=2)
        # Limpa quebras de linha e excesso de espaços
        resumo = re.sub(r'\s+', ' ', resumo)
        return resumo
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Existem várias opções para '{query}', tente ser mais específico."
    except wikipedia.exceptions.PageError:
        return None
    except Exception:
        return None

@app.route("/sms", methods=['POST'])
def sms_reply():
    mensagem = request.form.get('Body', '').strip()
    resp = MessagingResponse()

    # Mensagem educada padrão se não conseguir processar
    resposta = "Desculpe, não consegui entender. Pode perguntar novamente de forma diferente?"

    # Identificação do criador
    if "quem te criou" in mensagem.lower():
        resposta = (
            f"Fui criado por {CRIADOR['nome']}, "
            f"telefone: {CRIADOR['telefone']}, "
            f"email: {CRIADOR['email']}, "
            f"{CRIADOR['pais_parentes']}, "
            f"{CRIADOR['idade']} anos de idade."
        )
    # Informações privadas/legal
    elif any(x in mensagem.lower() for x in ["cpf", "nif", "documento", "senha", "informação legal"]):
        resposta = "Desculpe, não posso fornecer informações privadas ou legais."
    else:
        # Tenta Wikipedia primeiro
        wiki_res = busca_wikipedia(mensagem)
        if wiki_res:
            resposta = wiki_res
        else:
            # Busca no Google se não encontrou no Wikipedia
            resposta = busca_google(mensagem)

    resp.message(resposta)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

