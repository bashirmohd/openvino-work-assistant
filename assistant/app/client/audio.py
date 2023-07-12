import io
import threading
import time
import typing
import wave
from io import BytesIO

import numpy as np
import pyaudio
from numpy import ndarray


class AudioSystem:

    def __init__(self, buffer_size_seconds: int = 30) -> None:
        self.audio_sys = pyaudio.PyAudio()
        self.chunk = 4096
        self.channels = 1
        self.sample_rate = 16000
        self.sample_format = pyaudio.paInt16
        self.buffer_size_seconds = buffer_size_seconds
        self.buffer = []
        self.lock = threading.Lock()
        self.running = False
        self.background_task = threading.Thread(target=self.__run)
        self.background_task.start()

    def __del__(self) -> None:
        self.running = False
        self.background_task.join()
        self.audio_sys.terminate()

    def __run(self) -> None:
        stream = self.audio_sys.open(format=self.sample_format, channels=self.channels, rate=self.sample_rate,
                                     frames_per_buffer=self.chunk, input=True)

        max_buffer_size = self.buffer_size_seconds * self.sample_rate // self.chunk
        self.running = True
        while self.running:
            data = stream.read(self.chunk)
            with self.lock:
                self.buffer.append(data)

                # rework buffer every buffer_size_seconds to avoid many memory copies
                if len(self.buffer) > 2 * max_buffer_size:
                    self.buffer = self.buffer[-max_buffer_size:]

        stream.stop_stream()
        stream.close()

    def record_sound(self, seconds: int, raw_data: bool = False) -> ndarray | BytesIO:
        # wait specified seconds to capture the sound
        time.sleep(seconds)

        chunks_number = seconds * self.sample_rate // self.chunk
        with self.lock:
            buffer = self.buffer[-chunks_number:]

        data = np.array(b''.join(buffer))

        if raw_data:
            return np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0

        return self.audio_data_to_file(data)

    def play_sound(self, file: str | typing.IO) -> None:
        with wave.open(file, "rb") as sound:
            chunk = 4096

            stream = self.audio_sys.open(format=self.audio_sys.get_format_from_width(sound.getsampwidth()),
                                         channels=sound.getnchannels(),
                                         rate=sound.getframerate(), output=True)

            data = sound.readframes(chunk)
            while data:
                stream.write(data)
                data = sound.readframes(chunk)

        stream.close()

    def audio_data_to_file(self, data) -> BytesIO:
        if isinstance(data, np.ndarray) and data.dtype == "float32":
            data = (data * 32768).astype(np.int16).tobytes()
        file = io.BytesIO()
        with wave.open(file, "wb") as sample:
            sample.setnchannels(self.channels)
            sample.setsampwidth(self.audio_sys.get_sample_size(self.sample_format))
            sample.setframerate(self.sample_rate)
            sample.writeframes(data)

        file.seek(0)
        return file
