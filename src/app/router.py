from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel

from dependencies import get_toxicity_service
from service import ToxicityService


class MessageData(BaseModel):
    text: str


class ToxicityReport(BaseModel):
    toxicity_type: str


router = APIRouter()


@router.post("/forward")
def forward(message: MessageData, toxicity_service: ToxicityService = Depends(get_toxicity_service)):
    return ToxicityReport(toxicity_type=toxicity_service.get_toxicity_type(message.text))


@router.get("/history")
def get_history():
    # TODO: реализовать получение истории
    return "ok"


@router.delete("/history")
def delete_history():
    # TODO: реализовать удаление истории
    return "ok"


@router.get("/history/stats")
def get_stats():
    # TODO: реализовать получение статистики
    return "ok"
