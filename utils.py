import openai

openai.api_key = 'SUA_API_KEY_AQUI'  # Substitua pela sua chave

def responder_chatbot(pergunta):
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": pergunta}]
        )
        return resposta['choices'][0]['message']['content'].strip()
    except Exception as e:
        return "Desculpe, ocorreu um erro ao tentar responder."
