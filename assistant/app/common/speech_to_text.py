import logging as log
from typing import Union

import numpy as np
import whisper


class SpeechToTextModel:

    def __init__(self, model_name: str = "base", device: str = "cpu") -> None:
        self.model = whisper.load_model(model_name, device=device)
        self.no_speech_prob_threshold = 0.8

    def decode(self, audio: Union[str, np.ndarray]) -> str:
        result = self.model.transcribe(audio)
        if result["text"] == "" or result["segments"][0]["no_speech_prob"] > self.no_speech_prob_threshold:
            return ""

        log.info(f"Decoded text: {result['text']}")
        return result["text"]


def get_model(model_name: str = "base", device: str = "cpu") -> SpeechToTextModel:
    return SpeechToTextModel(model_name, device)
