from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel

from app.dependencies import get_toxicity_service, get_session
from app.service import ToxicityService
from .models.base import ToxicityType
from sqlalchemy.orm import Session

from datetime import datetime



class MessageData(BaseModel):
    text: str


class ToxicityReport(BaseModel):
    toxicity_type: str


class ForwardCallSchema(BaseModel):
    id: int
    start_time: datetime
    finish_time: datetime
    message: str
    result: ToxicityType


router = APIRouter()


@router.post("/forward")
def forward(message: MessageData, 
            toxicity_service: ToxicityService = Depends(get_toxicity_service)):
    return ToxicityReport(toxicity_type=toxicity_service.get_toxicity_type(message.text))


@router.get("/history", response_model=list[ForwardCallSchema])
def get_history(toxicity_service: ToxicityService = Depends(get_toxicity_service)):
    # TODO: реализовать получение истории
    return toxicity_service.get_history()


@router.delete("/history")
def delete_history(toxicity_service: ToxicityService = Depends(get_toxicity_service)):
    # TODO: реализовать удаление истории
    return toxicity_service.delete_history()


@router.get("/history/stats")
def get_stats(toxicity_service: ToxicityService = Depends(get_toxicity_service)):
    # TODO: реализовать получение статистики
    return toxicity_service.get_stats()
