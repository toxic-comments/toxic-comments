from abc import ABC, abstractmethod
from enum import Enum
import spacy
from functools import lru_cache


class ToxicityType(str, Enum):
    INSULT = "INSULT"
    NORMAL = "NORMAL"
    OBSCENITY = "OBSCENITY"
    THREAT = "THREAT"

class BaseToxicityPredictor(ABC):
    @abstractmethod
    def predict(self, text: str) -> ToxicityType:
        pass



@lru_cache(maxsize=1)
def get_nlp(): # чтобы не создавать тяжелый объект для разных Preprocessor объектов, а использовать один и тот же
    return spacy.load("ru_core_news_md")

class Preprocessor:
    def __init__(self):
        self.nlp = get_nlp()
        self.allowed_punct = {'!', '?'}

    def clean_lemmatize_comment(self, comment: str) -> str:
        comment = comment.lower()
        cleaned = []
        for token in self.nlp(comment):
            if token.is_stop:
                continue
            if token.is_alpha:
                lemma = token.lemma_
                if len(lemma) < 3 or len(lemma) > 30:
                    continue
                else:
                    cleaned.append(lemma)
            elif token.is_punct:
                if token.text in self.allowed_punct:
                    cleaned.append(token.text)
            else:
                cleaned.append(token.text)
        return ' '.join(cleaned)