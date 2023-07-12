import logging as log
import tempfile
from urllib import parse

import numpy as np
import requests

from assistant.app.client import audio
from assistant.app.common import speech_to_text


def _get_server_response(url: str, data: dict = None, files: dict = None, temp_response: bool = True):
    try:
        response = requests.post(url, data=data, files=files)
        if response.status_code != 200:
            log.warning(f"The server returned {response.status_code} {response.reason}")
            return None

        if response.headers["Content-Type"] == "audio/wav":
            # get the generated reply
            tmp_file = tempfile.NamedTemporaryFile(delete=temp_response)
            tmp_file.write(response.content)
            tmp_file.seek(0)
            return tmp_file

        if response.headers["Content-Type"] == "text/plain":
            return response.content

        log.warning(f"The server returned {response.headers['Content-Type']} content which cannot be handled")
        return None
    except requests.exceptions.RequestException as e:
        log.error("Cannot connect to the server. Did you start the server app?")
        log.error(e)


class WorkAssistant:

    def __init__(self, server_address: str, silence_threshold: int = 3) -> None:
        self.chat_url = server_address
        self.silence_threshold = silence_threshold
        self.synthesize_url = parse.urljoin(server_address, "synthesize")
        self.transcribe_url = parse.urljoin(server_address, "transcribe")
        self.audio_sys = audio.AudioSystem()
        self.stt_model = speech_to_text.get_model("tiny.en")
        self.sound_files = {}
        self.__load_default_sounds()
        log.info("Waiting for the keyword...")

    def __load_default_sounds(self) -> None:
        self.sound_files["init"] = _get_server_response(self.synthesize_url, data={"text": "Yes?"})
        self.sound_files["sending"] = _get_server_response(self.synthesize_url, data={"text": "Let me find the answer"})

    def __status_info(self, sound_file: tempfile.TemporaryFile) -> None:
        self.audio_sys.play_sound(sound_file.name)

    def detect_keyword(self, keyword: str) -> bool:
        captured = self.audio_sys.record_sound(seconds=1, raw_data=True)
        text = self.stt_model.decode(captured)
        return keyword in text.lower()

    def chat(self) -> None:
        self.__status_info(self.sound_files["init"])
        log.info("Speak now!")

        # capture the query, wait 3s after the last word
        elapsed_time = 0
        silence_counter = 0
        audio_data = []
        while silence_counter < self.silence_threshold:
            captured_data = self.audio_sys.record_sound(seconds=1, raw_data=True)

            text = self.stt_model.decode(captured_data)
            if text == "":
                silence_counter += 1
            else:
                silence_counter = 0

            audio_data.append(captured_data)
            elapsed_time += 1

        # if only silence is detected
        if elapsed_time == silence_counter:
            return

        audio_data = self.audio_sys.audio_data_to_file(np.concatenate(audio_data[:-self.silence_threshold]))
        self.__status_info(self.sound_files["sending"])
        log.info("Wait for the response...")
        file = {"audio": audio_data}
        resp = _get_server_response(self.chat_url, files=file)

        if resp:
            # play it
            self.audio_sys.play_sound(resp)
