# The work assistant

## Server app

Run the server app first. The initialization time may be long (especially the first).

### Prerequisites

```shell
sudo apt install ffmpeg
```

### Run

```shell
python assistant/app/server/main.py
```

Wait until you see ` * Running on http://127.0.0.1:5000`.

## Client app

Then run the client app. It works in endless loop, capturing your voice for 5s, waiting for the response from the server and playing the generated answer.

### Prerequisites

```shell
sudo apt install portaudio19-dev
```

## Run

```shell
python assistant/app/client/main.py -s http://localhost:5000/
```