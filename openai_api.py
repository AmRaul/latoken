import openai
import configparser

config = configparser.ConfigParser()
config.read("configs.ini")

# Отправка в GPT
def get_openai_response(question, content):
    openai.api_key = config["Api"]["OPENAI_API_KEY"]

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


