from aiogram.utils.markdown import hlink
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from openai_api import get_openai_response
from rag import execute_js_with_selenium_async
from config import settings

# Логирование
logging.basicConfig(level=logging.INFO)

url = 'https://coda.io/@latoken/latoken-talent/culture-139'

content_culture = None

# Инициализация
bot = Bot(token=settings.TG_API)
dp = Dispatcher()

# Загрузка информации из файлов
with open('hackathon_info.txt', 'r', encoding='utf-8') as f:
    hackathon_info = f.read()

with open('latoken_info.txt', 'r', encoding='utf-8') as f:
    latoken_info = f.read()


def add_link(content):
    useful_links = "\n\nПолезные ссылки:\n"
    useful_links += hlink("Ссылка на тест",
                          "https://docs.google.com/forms/d/e/1FAIpQLSdlj5aA3fCgGri9GeFC4csj-ZiNKnmorRTHNGeiIJRIbKyUZw/viewform?usp=send_form") + "\n"
    useful_links += hlink("Регистрация на хакатон", "https://t.me/gpt_web3_hackathon/5280") + "\n"


    content += useful_links
    return content

async def questions(message, content_culture):
    await message.answer("Сейчас я задам тебе вопрос")
    combined_content = latoken_info + "\n\n" + content_culture + "\n\n" + hackathon_info

    question_gpt = get_openai_response('Придумай вопрос без пояснения,'
                                       'тестируя кандидата на понимание переданной информации.'
                                       'Ответь только вопросом', combined_content)

    await message.answer(question_gpt)
    # await bot.edit_message_text(
    #     text=question_gpt,
    #     chat_id=vai.chat.id,
    #     message_id=vai.message_id,
    #     parse_mode="HTML"
    # )



@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Я бот, который может рассказать тебе о хакатоне AIxWEB3 и о компании Latoken. Задавай вопросы!")


# Обработчик сообщений
@dp.message()
async def handle_message(message: Message):
    user_question = message.text.lower()
    thinking_message = await message.answer("Думаю...")
    global content_culture
    if content_culture is None:
        content_culture = await execute_js_with_selenium_async(url)

    if "хакатон" in user_question or "hackathon" in user_question:
        hackathon_answer = get_openai_response(user_question, hackathon_info)
        hackathon_answer = add_link(hackathon_answer)
        await bot.edit_message_text(
            text=hackathon_answer,
            chat_id=thinking_message.chat.id,
            message_id=thinking_message.message_id,
            parse_mode="HTML"
        )
    elif "latoken" in user_question or "латокен" in user_question:
        await bot.edit_message_text(
            text='Поиск....',
            chat_id=thinking_message.chat.id,
            message_id=thinking_message.message_id)

        combined_content = latoken_info + "\n\n" + content_culture

        latoken_answer = get_openai_response(user_question, combined_content)
        latoken_answer = add_link(latoken_answer)

        await bot.edit_message_text(
            text=latoken_answer,
            chat_id=thinking_message.chat.id,
            message_id=thinking_message.message_id,
            parse_mode="HTML"
        )
    else:
        await bot.edit_message_text(
            text='Поиск....',
            chat_id=thinking_message.chat.id,
            message_id=thinking_message.message_id)
        culturre_answer = get_openai_response(user_question, content_culture)
        culturre_answer = add_link(culturre_answer)
        await bot.edit_message_text(
            text=culturre_answer,
            chat_id=thinking_message.chat.id,
            message_id=thinking_message.message_id,
            parse_mode="HTML"
        )

    # Написать что сейчас будет тест и сделать запрос на создание теста
    # В функцию

    await questions(message,content_culture)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
