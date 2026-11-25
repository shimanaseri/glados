from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from glados.config import MODEL_NAME, OLLAMA_HOST, HISTORY_LIMIT, OLLAMA_TEMPERATURE, OLLAMA_NUM_PREDICT, MEMORY_FILE
from glados.persona import SYSTEM_PROMPT


def make_chat_client():
    """Create the Ollama client. Kept lazy so importing the CLI is inexpensive."""
    return ChatOllama(
        model=MODEL_NAME,
        base_url=OLLAMA_HOST,
        streaming=True,
        temperature=OLLAMA_TEMPERATURE,
        num_predict=OLLAMA_NUM_PREDICT,
    )


def stream_reply(history, user_input, client=None):
    """Yield text chunks from Ollama using the system persona and recent history."""
    trimmed = history[-HISTORY_LIMIT:] if HISTORY_LIMIT > 0 else []

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    if MEMORY_FILE.is_file():
        memory = MEMORY_FILE.read_text(encoding="utf-8").strip()
        if memory:
            messages.append(SystemMessage(content="Persistent user memory (editable in memory.md):\n" + memory))
    for role, text in trimmed:
        if role == "user":
            messages.append(HumanMessage(content=text))
        else:
            messages.append(AIMessage(content=text))
    messages.append(HumanMessage(content=user_input))

    for chunk in (client or make_chat_client()).stream(messages):
        content = chunk.content
        if isinstance(content, str) and content:
            yield content
