import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=20
)

LLM_MODEL = "gemini-3.6-flash"

SUMMARY_THRESHOLD = 5
KEEP_RECENT = 2


async def context_rolling_summary(existing_summary: str, message_to_compress: list) -> str:

    print ("\n[MEMORY MANAGER]: Comperssing the message to rolling summary")   
    system_prompt = ("You are expert content summarizer. You provide an executive summary for the content and return the summary with in 3 lines of code")
    user_prompt = ("You are expert summarizer you review the content and provides the executive summary of the provided content"
                   "Keep summary dense and keep it under 3 sentences"
                   f"[Existining Summary]: {existing_summary or None}"
                   f"[New Turns to Merge]: {message_to_compress}")

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content


async def manage_context_with_summary(message: list, summary: str) -> tuple[list, str]:

    turn = message[1:]

    if len(turn) <= SUMMARY_THRESHOLD:
        return message, summary

    
    summary_count = len(turn) - KEEP_RECENT
    slice_for_summary = turn[:summary_count]
    keep_recent = turn[summary_count:]

    summary_result = await context_rolling_summary(summary, slice_for_summary)

    print(f"\n[ ROLLING SUMMARY]: {summary_result}")

    rebuilt_context = [message[0], {"role": "assistant", "content": f"[ROLLING SUMMARY]: {summary_result}"}] + keep_recent

    return rebuilt_context, summary_result


async def bgyani_it_triage():
    print(f"[BGYANI TRIAGE]: Welcome to BGYANI Traiage: send exit or quit to break ...")

    turn_counter = 0
    message_for_llm =[{"role": "system", "content": "You are Bgyani Traige expert. Be direct and technical"}]
    rolling_summary =""

    while True:
        turn_counter += 1
        user_input = input(f"{turn_counter}|User: ")

        if user_input.lower().strip() in ["exit","quit"]:
            print("\n\n User has chosen to exit...\n")
            break

        message_for_llm.append({"role": "user", "content": user_input})
        message_for_llm, rolling_summary = await manage_context_with_summary(message_for_llm, rolling_summary)

        print(f"[DEBUG]: Sending {len(message_for_llm)} items to LLM (Summary active: {bool(rolling_summary)})")

        try:
            response = await client.chat.completions.create(
                model=LLM_MODEL,
                temperature=0.0,
                messages=message_for_llm
            )

            llm_content = response.choices[0].message.content

            print(f"BGYANI g: {llm_content}\n")
            message_for_llm.append({"role": "assistant", "content": llm_content})

        except Exception as e:
            print(f"[ERROR] {e}: has been encountered")

if __name__ == "__main__":
    asyncio.run(bgyani_it_triage())
        
