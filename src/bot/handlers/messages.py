from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.services.fastapi import api_service

router = Router()

@router.message()
async def handle_message(message: types.Message):
    if not message.text:
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id, 
        action="typing"
    )

    toxicity_class = await api_service.predict_toxicity(
        text=message.text, 
        telegram_id=message.from_user.id
    )

    if toxicity_class:
        await message.answer(
            f"Текст: {message.text}\n"
            f"Класс: {toxicity_class}"
        )
    else:
        await message.answer("Ошибка при обработке запроса.")