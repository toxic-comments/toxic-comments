from datetime import datetime

from app.auth.dependencies import get_current_user, require_admin
from app.database import User
from app.dependencies import get_toxicity_service, get_session
from app.service import ToxicityService
from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel

from .database import PredictedClass


class MessageData(BaseModel):
    text: str


class ToxicityReport(BaseModel):
    toxicity_type: str


class ForwardCallSchema(BaseModel):
    id: int
    start_time: datetime
    finish_time: datetime
    message: str
    result: PredictedClass


router = APIRouter()


@router.post("/forward")
def forward(message: MessageData,
           user: User = Depends(get_current_user), # тут будет ошибка если нет авторизации
           toxicity_service: ToxicityService = Depends(get_toxicity_service)):
    return ToxicityReport(toxicity_type=toxicity_service.get_toxicity_type(message.text))

@router.get("/history", response_model=list[ForwardCallSchema])
def get_history(toxicity_service: ToxicityService = Depends(get_toxicity_service),
               user: dict = Depends(require_admin)): # ошибка если пользователь не админ
    return toxicity_service.get_history()

@router.delete("/history")
def delete_history(toxicity_service: ToxicityService = Depends(get_toxicity_service),
                  user: dict = Depends(require_admin)): # ошибка если пользователь не админ
    return toxicity_service.delete_history()

@router.get("/history/stats")
def get_stats(toxicity_service: ToxicityService = Depends(get_toxicity_service),
             user: dict = Depends(require_admin)): # ошибка если пользователь не админ
    # TODO: реализовать получение статистики
    return toxicity_service.get_stats()
