from aiogram import Router, types
from aiogram.filters import Command
from bot.services.fastapi import api_service

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Сервис определения токсичности комментариев.\n"
        "В личном чате отправьте текст для проверки.\n"
        "В группе бот отвечает только на токсичные сообщения.\n"
        "Доступные классы: INSULT, NORMAL, OBSCENITY, THREAT"
    )

@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "Команды:\n"
        "/start - Начать работу\n"
        "/help - Справка\n"
        "/predict - Анализ текста (использовать как ответ на сообщение)\n"
        "В группе бот автоматически анализирует текстовые сообщения."
    )

@router.message(Command("predict"))
async def predict_command(message: types.Message):
    if not message.reply_to_message or not message.reply_to_message.text:
        await message.answer(
            "Команда должна быть ответом на текстовое сообщение."
        )
        return

    text_to_analyze = message.reply_to_message.text
    toxicity_class = await api_service.predict_toxicity(
        text=text_to_analyze, 
        telegram_id=message.from_user.id
    )

    if toxicity_class:
        await message.answer(
            f"Текст: {text_to_analyze}\n"
            f"Класс: {toxicity_class}"
        )
    else:
        await message.answer("Ошибка при обработке запроса.")
