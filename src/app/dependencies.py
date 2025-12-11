from fastapi.params import Depends
from sqlalchemy.orm import Session

from database import engine
from inference import ToxicityPredictor
from service import ToxicityService


def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def get_predictor():
    return ToxicityPredictor()


def get_toxicity_service(
        session: Session = Depends(get_session),
        predictor: ToxicityPredictor = Depends(get_predictor)
):
    return ToxicityService(session, predictor)
