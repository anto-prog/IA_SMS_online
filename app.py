from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import wikipedia
from bs4 import BeautifulSoup

app = Flask(__name__)

# Configura Wikipedia para usar html.parser
wikipedia.set_lang("pt")

@app.route("/sms", methods=['POST'])
def sms_reply():
    try:
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        print(f"[INFO] Mensagem recebida de {from_number}: {incoming_msg}")

        resp = MessagingResponse()
        msg = resp.message()

        # Resposta padrão educada
        if not incoming_msg:
            msg.body("Não recebi nenhuma mensagem. Por favor, envie algo.")
        elif "quem te criou" in incoming_msg.lower():
            msg.body(
                "Foi criado por António Zacarias Manuel. "
                "Telefone: 948404462, Email: azmanuel@gmail.com, "
                "Filho de Domingos António Manuel e Jany Paulo Manuel, 17 anos."
            )
        elif "mess" in incoming_msg.lower():  # exemplo de perguntas sobre Messi
            msg.body("Messi é um jogador de futebol argentino muito famoso.")
        else:
            # Tenta buscar no Wikipedia
            try:
                result = wikipedia.summary(incoming_msg, sentences=2)
                msg.body(result)
            except wikipedia.exceptions.DisambiguationError as e:
                msg.body(f"Existem várias opções para '{incoming_msg}': {e.options[:5]}")
            except wikipedia.exceptions.PageError:
                msg.body(f"Desculpe, não encontrei informações sobre '{incoming_msg}'.")
            except Exception as e:
                print(f"[ERRO] Wikipedia ou outro erro: {e}")
                msg.body("Não consegui processar a sua mensagem agora, tente novamente.")

        print(f"[INFO] Respondendo: {msg.body}")
        return str(resp)
    except Exception as e:
        print(f"[ERRO] Falha geral no /sms: {e}")
        return Response("Erro interno", status=500)

if __name__ == "__main__":
    print("Servidor Flask rodando...")
    app.run(host="0.0.0.0", port=5000)