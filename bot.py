import os
import json
from aiogram.utils.markdown import hlink
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from openai_api import get_openai_response
from rag import execute_js_with_selenium_async
import configparser

class TestState(StatesGroup):
    waiting_for_answer = State()


logging.basicConfig(level=logging.INFO)

url = 'https://coda.io/@latoken/latoken-talent/culture-139'

content_culture = None
config = configparser.ConfigParser()
config.read("configs.ini")


bot = Bot(token=config["Api"]["TG_API"])
dp = Dispatcher()


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

def get_test_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Начать тест", callback_data="start_test")]
        ]
    )

async def load_content():
    global content_culture
    file_path = 'content_culture.json'

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content_culture = json.load(f)
        logging.info("Загружено содержимое из файла.")
    else:
        # Если файл не существует, загружаем данные и сохраняем их
        content_culture = await execute_js_with_selenium_async(url)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content_culture, f)
        logging.info("Содержимое загружено и сохранено в файл.")


@dp.callback_query(F.data == "start_test")
async def start_test(callback: CallbackQuery, state: FSMContext):
    # global is_testing
    # is_testing = True
    message = callback.message
    await message.answer("Тест начат! Напишите 'стоп', чтобы завершить тест.")


    combined_content = latoken_info + "\n\n" + content_culture + "\n\n" + hackathon_info
    questions = []

    while len(questions) < 3:
        question =  get_openai_response(
            "Придумай вопрос без пояснения, тестируя кандидата на понимание переданной информации. Ответь только вопросом",
            combined_content
        )

        if question not in questions:
            questions.append(question)

    await state.update_data(questions=questions, current_index=0)

    await message.answer(questions[0])
    await state.set_state(TestState.waiting_for_answer)



@dp.message(TestState.waiting_for_answer)
async def process_answer(message: Message, state: FSMContext):
    combined_content = latoken_info + "\n\n" + content_culture + "\n\n" + hackathon_info
    user_data = await state.get_data()
    questions = user_data["questions"]
    current_index = user_data["current_index"]

    if message.text.lower() == "стоп":
        await message.answer("Тест завершен.")
        await state.clear()
        return


    evaluation = get_openai_response(
        f"Оцени следующий ответ на вопрос: '{questions[current_index]}'. Ответ: '{message.text}'",combined_content
    )
    await message.answer(f"Оценка ответа: {evaluation}")

    # Переход к следующему вопросу
    current_index += 1
    if current_index < len(questions):
        await state.update_data(current_index=current_index)
        await message.answer(questions[current_index])
    else:
        await message.answer("Тест завершен. Спасибо за участие!")
        await state.clear()

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Я бот, который может рассказать тебе о хакатоне AIxWEB3 и о компании Latoken. Задавай вопросы!"
    , reply_markup=get_test_keyboard())
    

    keyboard = InlineKeyboardMarkup()
    test_button = InlineKeyboardButton("Начать тест", callback_data="start_test")
    keyboard.add(test_button)
    
    await message.answer("Нажмите кнопку, чтобы начать тест:", reply_markup=keyboard)

@dp.callback_query()
async def handle_test_start(callback_query):
    await callback_query.answer()
    await start_test(callback_query.message)


@dp.message()
async def handle_message(message: Message):
    global is_testing
    user_question = message.text.lower()

    thinking_message = await message.answer("Думаю...")
    
    if content_culture is None:
        await message.answer("Загрузка контента, пожалуйста, подождите...")
        await load_content()  # Загружаем контент, если он еще не загружен

    if "хакатон" in user_question or "hackathon" in user_question:
        hackathon_answer = get_openai_response(user_question, hackathon_info)
        hackathon_answer = add_link(hackathon_answer)
        await bot.edit_message_text(
            text=hackathon_answer,
            chat_id=thinking_message.chat.id,
            message_id=thinking_message.message_id,
            parse_mode="HTML",
            reply_markup=get_test_keyboard()
        )
    elif "latoken" in user_question or "латокен" in user_question:
        await bot.edit_message_text(
            text='Поиск....',
            chat_id=thinking_message.chat.id,
            message_id=thinking_message.message_id),


        combined_content = latoken_info + "\n\n" + content_culture

        latoken_answer = get_openai_response(user_question, combined_content)
        latoken_answer = add_link(latoken_answer)

        await bot.edit_message_text(
            text=latoken_answer,
            chat_id=thinking_message.chat.id,
            message_id=thinking_message.message_id,
            parse_mode="HTML",
            reply_markup=get_test_keyboard()
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
            parse_mode="HTML",
            reply_markup=get_test_keyboard()
        )


async def main():
    await load_content()  # Запускаем загрузку контента при запуске
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
