from aiogram import Router, types
from bot.services.fastapi import api_service

router = Router()

GROUP_CHAT_TYPES = {"group", "supergroup"}
TOXICITY_CLASSES = {"INSULT", "OBSCENITY", "THREAT"}


def _get_telegram_id(message: types.Message) -> int:
    """Возвращает стабильный id отправителя для API."""
    if message.from_user:
        return message.from_user.id
    if message.sender_chat:
        return message.sender_chat.id
    return message.chat.id


def _is_toxic(toxicity_class: str | None) -> bool:
    if not toxicity_class:
        return False
    return toxicity_class.upper() in TOXICITY_CLASSES


@router.message()
async def handle_message(message: types.Message):
    text = message.text or message.caption
    if not text:
        return
    if message.from_user and message.from_user.is_bot:
        return
    if text.startswith("/"):
        return

    is_group_chat = message.chat.type in GROUP_CHAT_TYPES

    if not is_group_chat:
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action="typing"
        )

    toxicity_class = await api_service.predict_toxicity(
        text=text,
        telegram_id=_get_telegram_id(message)
    )

    if is_group_chat:
        if _is_toxic(toxicity_class):
            await message.reply(f"Класс токсичности: {toxicity_class}")
        return

    if not toxicity_class:
        await message.answer("Ошибка при обработке запроса.")
        return

    await message.answer(
        f"Текст: {text}\n"
        f"Класс: {toxicity_class}"
    )
