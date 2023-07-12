import logging as log
import tempfile

import flask

from assistant.app.common import speech_to_text, text_to_speech, chat

app = flask.Flask(__name__)
stt_model = speech_to_text.get_model("base.en")
tts_model = text_to_speech.get_model()
chat_model = chat.get_model()


@app.route("/", methods=["POST"])
def chat():
    with tempfile.NamedTemporaryFile() as fp:
        filename = fp.name

        wav_file = flask.request.files["audio"]
        wav_file.save(filename)
        query = stt_model.decode(filename)

    reply = chat_model.respond(query)
    fp = tts_model.encode(reply)
    return flask.send_file(fp.name, mimetype="audio/wav", download_name="result", as_attachment=True)


@app.route("/transcribe", methods=["POST"])
def transcribe():
    with tempfile.NamedTemporaryFile() as fp:
        filename = fp.name

        wav_file = flask.request.files["audio"]
        wav_file.save(filename)

        return stt_model.decode(filename)


@app.route("/synthesize", methods=["POST"])
def synthesize():
    text = flask.request.form["text"]
    fp = tts_model.encode(text)
    return flask.send_file(fp.name, mimetype="audio/wav", download_name="result", as_attachment=True)


if __name__ == "__main__":
    log.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=log.INFO, datefmt='%Y-%m-%d %H:%M:%S')

    app.run()
