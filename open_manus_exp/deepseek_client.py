
from langchain_deepseek import ChatDeepSeek

import getpass
import os

if not os.getenv("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter your DeepSeek API key: ")

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=3,
)


messages = [
    (
        "system",
        "You are a helpful assistant ",
    ),
    ("human", "tell me what model you are"),
]
ai_msg = llm.invoke(messages)
print(ai_msg.content)
