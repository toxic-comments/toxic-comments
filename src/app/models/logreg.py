from joblib import load
from .base import BaseToxicityPredictor, ToxicityType, Preprocessor
from pathlib import Path


class LogRegPredictor(BaseToxicityPredictor):
    # убедитесь что модель загружена из DVC
    # и надо понять как прописать путь к модели
    def __init__(self, model_path: Path):
        self.model = load(model_path)
        self._classes = self._build_class_mapping()
        self.preprocessor = Preprocessor()


    def _build_class_mapping(self) -> dict:
        """
        Строит отображение выхода sklearn → ToxicityType. 
        При необходимости тут задаются соотвествия между выходами модели и нашими классами токсичности
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

if __name__ == "__main__":
    model = LogRegPredictor(model_path="models/logreg_bow_100k_C1.joblib")
    print(model.predict('ты молодец'))
    print(model.predict('ты лох'))
    print(model.predict('я б вдул'))
    print(model.predict('я убью тебя'))