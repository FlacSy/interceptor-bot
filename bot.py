import json
from aiogram import types
from config import channel_a_id, channel_b_id, allowed_user
from create_bot import dp, bot
import os
from aiogram.types import BotCommand
import asyncio
import aiohttp

if not os.path.isfile('keywords.json'):
    with open('keywords.json', 'w') as file:
        json.dump([], file)

# Загрузка списка ключевых слов из файла
with open('keywords.json', 'r') as file:
    keywords = json.load(file)

@dp.message_handler(commands=['addword'])
async def add_keyword(message: types.Message):
    if message.from_user.username == allowed_user:
        args = message.get_args().lower()
        if args:
            keywords.append(args)
            with open('keywords.json', 'w') as file:
                json.dump(keywords, file)
            await message.reply(f"Ключевое слово '{args}' успешно добавлено.")
        else:
            await message.reply("Вы не указали ключевое слово.")
    else:
        await message.reply("У вас нет доступа к этой команде.")

@dp.message_handler(commands=['removeword'])
async def remove_keyword(message: types.Message):
    if message.from_user.username == allowed_user:
        args = message.get_args().lower()
        if args:
            if args in keywords:
                keywords.remove(args)
                with open('keywords.json', 'w') as file:
                    json.dump(keywords, file)
                await message.reply(f"Ключевое слово '{args}' успешно удалено.")
            else:
                await message.reply(f"Ключевое слово '{args}' не найдено.")
        else:
            await message.reply("Вы не указали ключевое слово.")
    else:
        await message.reply("У вас нет доступа к этой команде.")

@dp.message_handler(commands=['wordlist'])
async def list_keywords(message: types.Message):
    if message.from_user.username == allowed_user:
        if keywords:
            keyword_list = '\n'.join(keywords)
            await message.reply(f"Список ключевых слов:\n{keyword_list}")
        else:
            await message.reply("Список ключевых слов пуст.")
    else:
        await message.reply("У вас нет доступа к этой команде.")

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: types.Message):
    if message.chat.id == channel_a_id and any(keyword in message.text.lower() for keyword in keywords):
        await bot.send_message(chat_id=channel_b_id, text=message.text)

async def set_bot_commands():
    commands = [
        BotCommand(command='/removeword', description='Удаление ключевого слова'),
        BotCommand(command='/addword', description='Добавление ключевого слова'),
        BotCommand(command='/wordlist', description='Список слов')
    ]
    await bot.set_my_commands(commands)

async def on_startup(dp):
    await set_bot_commands()
    print('Бот запущен')
async def on_shutdown(dp):
    await bot.close()
    await bot.session.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(on_startup(dp))
    try:
        loop.run_until_complete(dp.start_polling())
    finally:
        loop.run_until_complete(on_shutdown(dp))
        loop.close()
