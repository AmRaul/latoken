import openai
from config import settings

# Отправка в GPT
def get_openai_response(question, content):
    openai.api_key = settings.OPENAI_API_KEY


    # Формируем сообщение
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Here's some content from the site: {content}"},
        {"role": "user", "content": f"User question: {question}"}
    ]

    # Запрос
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1500
    )

    return response.choices[0].message.content.strip()


