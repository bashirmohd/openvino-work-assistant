import tempfile
from typing import Union

import numpy as np
from TTS import api as tts


class TextToSpeechModel:

    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC_ph", device: str = "cpu") -> None:
        self.model = tts.TTS(model_name, gpu=device == "gpu")

    def encode(self, text: str) -> Union[tempfile.TemporaryFile, np.ndarray]:
        temp_file = tempfile.NamedTemporaryFile()
        self.model.tts_to_file(text, file_path=temp_file.name)
        return temp_file


def get_model(model_name: str = "tts_models/en/ljspeech/tacotron2-DDC_ph", device: str = "cpu") -> TextToSpeechModel:
    return TextToSpeechModel(model_name, device)
