import argparse
import logging as log

from assistant.app.client import client


def run(server_address):
    assistant = client.WorkAssistant(server_address, silence_threshold=2)

    while True:
        if assistant.detect_keyword("hello"):
            assistant.chat()


if __name__ == "__main__":
    log.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=log.INFO, datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", type=str, default="http://localhost:5000/", help="Address of the sever")
    args = parser.parse_args()

    run(args.server)
