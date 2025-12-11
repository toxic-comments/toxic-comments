from datetime import datetime

from sqlalchemy.orm import Session

from database import ForwardCall
from inference import ToxicityPredictor


class ToxicityService:

    def __init__(self, session: Session, predictor: ToxicityPredictor):
        self.session = session
        self.predictor = predictor

    def get_toxicity_type(self, text: str):
        start = datetime.now()
        toxicity_type = self.predictor.predict(text)
        end = datetime.now()

        # TODO: добавить сохранение еще каких-нибудь параметров запроса
        forward_call = ForwardCall(start_time=start, finish_time=end)
        self.session.add(forward_call)
        self.session.commit()

        return toxicity_type
