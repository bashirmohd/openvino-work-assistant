import transformers


class ChatModel:

    def __init__(self, model_name: str = "databricks/dolly-v2-3b", device: str = "cpu") -> None:
        self.model = transformers.pipeline(model=model_name, trust_remote_code=True, device=device)

    def respond(self, prompt: str) -> str:
        return self.model(prompt)[0]["generated_text"]


def get_model(model_name: str = "databricks/dolly-v2-3b", device: str = "cpu") -> ChatModel:
    return ChatModel(model_name, device)
