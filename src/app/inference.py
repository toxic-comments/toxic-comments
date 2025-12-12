
class ToxicityType:
    NORMAL = "NORMAL"
    INSULT = "INSULT"
    THREAT = "THREAT"
    OBSCENITY = "OBSCENITY"


class ToxicityPredictor:

    def predict(self, text: str) -> str:
        # TODO: реализовать вызов пайплана и классификатора
        return ToxicityType.NORMAL



