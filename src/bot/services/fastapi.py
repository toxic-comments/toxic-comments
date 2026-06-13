import logging
import httpx
from bot.config import settings

logger = logging.getLogger(__name__)

class FastAPIService:
    def __init__(self):
        self.url = f"{settings.FASTAPI_SERVICE_URL}/forward"
        self.timeout = settings.FASTAPI_TIMEOUT
        self.headers = {"X-API-Key": settings.INTERNAL_API_KEY}
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def predict_toxicity(self, text: str, telegram_id: int) -> str | None:
        if not text.strip():
            return None
            
        headers = {**self.headers, "X-Telegram-Id": str(telegram_id)}
        
        try:
            response = await self.client.post(
                self.url,
                json={"text": text},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("toxicity_type")
        except httpx.HTTPStatusError as e:
            logger.error(f"API HTTP Error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"API Connection Error: {e.__class__.__name__}")
            return None

    async def close(self):
        await self.client.aclose()

api_service = FastAPIService()