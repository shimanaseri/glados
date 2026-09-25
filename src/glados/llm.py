from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from glados.configs import MODEL_NAME, OLLAMA_HOST, HISTORY_LIMIT
from glados.persona import SYSTEM_PROMPT


glados_core = ChatOllama(model=MODEL_NAME, base_url=OLLAMA_HOST, streaming=True)

def stream_reply(history, user_input):
    trimmed = history[-HISTORY_LIMIT:]

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for role, text in trimmed:
        if role == "user":
            messages.append(HumanMessage(content=text))
        else:
            messages.append(AIMessage(content=text))
    messages.append(HumanMessage(content=user_input))

    for chunk in glados_core.stream(messages):
        yield chunk.content