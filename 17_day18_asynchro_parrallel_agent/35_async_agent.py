import os
import json
import asyncio
import time 
from dotenv import load_dotenv
from openai import AsyncOpenAI #<-- OpenAi compatible with Async 

#Setup and configuration
load_dotenv()
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=20
)

LLM_MODEL = "gemini-3.6-flash"

#defining async tool

async def check_monitor_async(app_name: str) -> str:
    print(f"--- [Network]: Quering the DB to check the {app_name} status")
    await asyncio.sleep(2) #simulating the real world delays
    return f"[RESULT]: The {app_name} is marked down with ERR_503"

async def search_runbook_async(err_code: str) -> str:
    print(f"----[Network]: Checking the RUNBOOK for {err_code}")
    await asyncio.sleep(2)
    return f"{err_code} requires a server restart"

monitor_tool = {
    "type": "function",
    "function": {
        "name": "check_monitor_async",
        "description": "It checks the status of the running application along with error code if any",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                }
            },
            "required": ["app_name"]
        }
    }
}

search_tool = {
    "type": "function",
    "function": {
        "name": "search_runbook_async",
        "description": "It searches the runbook (db) for any specific error and provide the steps to address the issue",
        "parameters": {
            "type": "object",
            "properties": { "err_code": {"type": "string"}},
            "required": ["err_code"]
        }
    }
}

# The real Async agent
async def bgyani_g_triage(user_prompt: str) -> str:
    print("[BGYANI G] Initializing the Bgyani Triage services ....")

    message_for_llm = [
        {"role":"system", "content": "You are BGYANI G TRIAGE. The user will ask many queries. Please use tools to perform the actions. you must run the tools in parrallel if multiple things are asked"},
        {"role": "user", "content": user_prompt}
    ]

#await is used because AsyncOpenAI and make the resources free while it is waiting for the response from llm
    response = await client.chat.completions.create(
        model=LLM_MODEL,
        tools=[monitor_tool, search_tool],
        temperature=0.0,
        messages=message_for_llm
    )

    message = response.choices[0].message
    message_for_llm.append(message)

    if message.tool_calls:
        print(f"[LLM DECISION]: Agent requested {len(message.tool_calls)} in parrallel")

        # Phase1: Gathering 
        pending_task = []
        task_metadata = []

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if func_name == "check_monitor_async":
                app_data = check_monitor_async(app_name=arguments.get("app_name",""))
                pending_task.append(app_data)
                task_metadata.append({"id":tool_call.id, "name": func_name})

            elif func_name == "search_runbook_async":
                app_data = search_runbook_async(err_code=arguments.get("err_code",""))
                pending_task.append(app_data)
                task_metadata.append({"id":tool_call.id, "name": func_name})

        #Phase 2: Execution
        print("\n [EXECUTION]:Firing all the tasks simulteneously")
        start_time = time.time()

        print(f"\n\n [PENDING TASK]: {pending_task}\n\n")

        results = await asyncio.gather(*pending_task,return_exceptions=True)

        stop_time = time.time()

        print(f"[EXECUTION]: completed it tool {stop_time - start_time:.1f} seconds (sequential would take 4.0s+)")

        for i, result in enumerate(results):
            meta_data = task_metadata[i]

            if isinstance(result, Exception):
                final_content = str(result)
            else:
                final_content = result

            message_for_llm.append(
                {"role": "tool", "tool_call_id": meta_data["id"], "name": meta_data["name"], "content": str(final_content)}
            )

            print(f"--> Attached receipt {meta_data['id']}")

        #--- FINAL SUMMARISE TO LLM ----
        print("[LLM]: sending parrallel result for summary ...")
        final_response = await client.chat.completions.create(
            model=LLM_MODEL,
            temperature=0.0,
            tools=[monitor_tool, search_tool],
            messages=message_for_llm
        )
        print(f"[GYANI G FINAL RESULT]: {final_response.choices[0].message.content}")

# ENGINE STARTER

if __name__ == "__main__":
    prompt = "Check the monitoring for payment_gateway, and also search the runbook for ERR_503."

    asyncio.run(bgyani_g_triage(prompt))






