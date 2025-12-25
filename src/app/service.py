from datetime import datetime
from email import message

from sqlalchemy.orm import Session

from app.database import ForwardCall
#from app.inference import ToxicityPredictor
from app.models.base import BaseToxicityPredictor

from datetime import timedelta
from fastapi import HTTPException

from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
import numpy as np

class DistributionStats(BaseModel):
    mean_: float
    p50: float
    p95: float
    p99: float


class StatsResponse(BaseModel):
    count_: int
    processing_time: Optional[DistributionStats]
    message_length: Optional[DistributionStats]
    token_count: Optional[DistributionStats]



class ToxicityService:
    def __init__(self, session: Session, predictor: BaseToxicityPredictor): # немного исправил, теперь класс ожидает на вход произвольную модель, наследницу BaseToxicityPredictor
        self.session = session
        self.predictor = predictor

    def get_toxicity_type(self, text: str):
        start = datetime.now()

        if not isinstance(text, str):
            raise HTTPException(status_code=400, detail="bad request")
        
        try:
            toxicity_type = self.predictor.predict(text)
        except Exception as e:
            raise HTTPException(status_code=403, detail="модель не смогла обработать данные")
        
        end = datetime.now()

        forward_call = ForwardCall(start_time=start, finish_time=end, message=text, result=toxicity_type)
        self.session.add(forward_call)
        self.session.commit()

        return toxicity_type
    
    def get_history(self):
        return (self.session.query(ForwardCall)
            .order_by(ForwardCall.id.desc())
            .all()
        )
    
    def delete_history(self):
        for forward_call in self.get_history():
            self.session.delete(forward_call)
        self.session.commit()





    def _compute_distribution(self, values: list[float]) -> DistributionStats:
        arr = np.array(values)

        return DistributionStats(
            mean_=float(arr.mean()),
            p50=float(np.percentile(arr, 50)),
            p95=float(np.percentile(arr, 95)),
            p99=float(np.percentile(arr, 99)),
        )


    def get_stats(self) -> StatsResponse:
        history = self.get_history()
        # print(history)
        if not history or len(history) == 0:
            return StatsResponse(
                count_=0,
                processing_time=None,
                message_length=None,
                token_count=None
            )

        processing_times = []
        message_lengths = []
        token_counts = []

        for fc in history:
            # время обработки в секундах
            duration = (fc.finish_time - fc.start_time).total_seconds()
            processing_times.append(duration)

            # длина сообщения
            message_lengths.append(len(fc.message))

            # количество токенов = слов
            token_counts.append(len(fc.message.split()))

        return StatsResponse(
            count_=len(history),
            processing_time=self._compute_distribution(processing_times),
            message_length=self._compute_distribution(message_lengths),
            token_count=self._compute_distribution(token_counts),
            )