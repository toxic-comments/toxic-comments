import warnings

from joblib import load
from sklearn.exceptions import InconsistentVersionWarning

from .base import BaseToxicityPredictor, ToxicityType, Preprocessor
from pathlib import Path


class LogRegPredictor(BaseToxicityPredictor):
    def __init__(self, model_path: Path):
        self.model = self._load_model(model_path)
        self._classes = self._build_class_mapping()
        self.preprocessor = Preprocessor()

    @staticmethod
    def _load_model(model_path: Path):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
            return load(model_path)

    def _build_class_mapping(self) -> dict:
        """
        Строит отображение выхода sklearn → ToxicityType. 
        При необходимости тут задаются соответствия между выходами модели и нашими классами токсичности
        """
        mapping = {}

        for cls in self.model.classes_:
            try:
                mapping[cls] = ToxicityType(cls)
            except ValueError:
                raise ValueError(
                    f"Unknown model class '{cls}'. "
                    f"Expected one of {[t.value for t in ToxicityType]}"
                )

        return mapping

    def predict(self, text: str) -> str:
        # предобработка текста
        text = self.preprocessor.clean_lemmatize_comment(text)
        
        if not text:
            return ToxicityType.NORMAL
        
        # предсказание и маппинг к ToxicityClass
        pred = self.model.predict([text])[0]
        return self._classes[pred]
