from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.database import engine
from app.models.base import BaseToxicityPredictor
from app.models.logreg import LogRegPredictor
from app.service import ToxicityService
from functools import lru_cache
import os

MODEL_DIR = os.getenv("MODEL_DIR", "models/logreg_bow_100k_C1.joblib")

def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


@lru_cache(maxsize=1) # при первом старте модель создается, потом просто берется из кэша
def get_predictor():
    model_name = os.environ.get("MODEL_NAME", "logreg")
    if model_name == "logreg":
        predictor = LogRegPredictor(model_path=MODEL_DIR)
        return predictor
    # в будущем сюда добавляем инициализацию других моделей) Они обязательно должны наследоваться от BaseToxicityPredictor
    else:
        raise ValueError(f"Unknown model: {model_name}")


def get_toxicity_service(
        session: Session = Depends(get_session),
        predictor: BaseToxicityPredictor = Depends(get_predictor)
):
    return ToxicityService(session, predictor)
