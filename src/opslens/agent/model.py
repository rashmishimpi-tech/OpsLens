from langchain_ollama import ChatOllama


def get_model() -> ChatOllama:
    return ChatOllama(
        model="qwen2.5:3b",
        temperature=0,
    ) 