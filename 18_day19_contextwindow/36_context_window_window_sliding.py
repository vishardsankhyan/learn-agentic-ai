import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=20
)

MAX_COUNT = 6 #1: SYSTEM PROMPT and 5 TURN FOR USER
LLM_MODEL = "gemini-3.6-flash"


def enforce_sliding_window(messages: list) -> list:
    if len(messages) <= MAX_COUNT:
        return messages

#Keep the system prompt and grab most recent (MAX -1) messages
    system_prompt = messages[0]
    recent_messages = messages[-(MAX_COUNT - 1):]
    return [system_prompt] + recent_messages


async def bgyani_chat_session():
    message_for_llm=[{"role": "system", "content": "you are expert chat management agent. You review the user chat and respond back eventfully"}]

    counter = 0

    while True:

        user_prompt = input("[BGYANI CHAT - exit|quit ] You: ")

        if user_prompt.lower() in ['exit', 'quit']:
            print("\n User wants to exit the session\n Bye Bye...\n")
            break

        message_for_llm.append({"role": "user", "content": user_prompt})
        message_for_llm = enforce_sliding_window(message_for_llm)

        try:

            response = await client.chat.completions.create(
                model=LLM_MODEL,
                temperature=0.0,
                messages=message_for_llm
            )

            content = response.choices[0].message.content
            print("[BGYANI CHAT] GYANI G: ", content)
            message_for_llm.append({"role": "assistant", "content": content})

        except Exception as e:
            print(f"[ERROR]: has been occurred {str(e)}")

        counter += 1

if __name__ == "__main__":
    asyncio.run(bgyani_chat_session())

