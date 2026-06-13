import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import settings
from bot.handlers import commands, messages
from bot.services.fastapi import api_service

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

async def on_shutdown(dp: Dispatcher):
    """Действия при остановке бота."""
    await api_service.close()

async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(commands.router)
    dp.include_router(messages.router)

    dp.shutdown.register(on_shutdown)

    logger.info("Запуск бота...")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")