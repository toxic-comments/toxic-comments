from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.database import engine
#from app.inference import ToxicityPredictor
from app.models.base import BaseToxicityPredictor
from app.models.logreg import LogRegPredictor
from app.service import ToxicityService
from functools import lru_cache
import os



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
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # src/app -> project_root
        model_path = os.path.join(BASE_DIR, "../models", "logreg_bow_100k_C1.joblib")
        predictor = LogRegPredictor(model_path=model_path)
        return predictor
    # в будущем сюда добавляем инициализацию других моделей) Они обязательно должны наследоваться от BaseToxisityPredictor
    else:
        raise ValueError(f"Unknown model: {model_name}")


def get_toxicity_service(
        session: Session = Depends(get_session),
        predictor: BaseToxicityPredictor = Depends(get_predictor)
):
    return ToxicityService(session, predictor)
