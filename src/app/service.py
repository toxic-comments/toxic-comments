from datetime import datetime
from email import message

from sqlalchemy.orm import Session

from app.database import ForwardCall
#from app.inference import ToxicityPredictor
from app.models.base import BaseToxicityPredictor

from datetime import timedelta
from fastapi import HTTPException


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

        # TODO: добавить сохранение еще каких-нибудь параметров запроса
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
        return 'deleted'
    
    def get_stats(self):
        history = self.get_history()
        if not history:
            return {
                "count": 0,
                "average": None
            }

        total = sum(
            (fc.finish_time - fc.start_time for fc in history),
            timedelta()
        )

        return {
            "count": len(history),
            "average": total / len(history)
        }