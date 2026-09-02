import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def check_db_connection(db_instance: str) -> str:
    return f" The db instance {db_instance} has 53 current connections"

def get_slow_queries(db_instance: str) -> str:
    return f" The db instance {db_instance} has 5 queries over 1 minute"

connection_tool = {
    "type": "function",
    "function": {
        "name": "check_db_connection",
        "description": "Function provides current connections on a db ",
        "parameters": {
            "type": "object",
            "properties": {
                "db_instance": {
                    "type": "string",
                    "description": "It represents the db_instance details"
                }
            },
            "required": ["db_instance"]
        }
    }
}

queries_tool = {
    "type": "function",
    "function": {
        "name": "get_slow_queries",
        "description": "It provides the list of queries which are slow",
        "parameters": {
            "type": "object",
            "properties": {
                "db_instance": {
                    "type": "string",
                    "description": "It represents the db instance "
                }
            },
            "required": ["db_instance"]

        }
    }
}

tool_dispatcher = {
    'get_slow_queries': get_slow_queries,
    'check_db_connection': check_db_connection
}


def llm_call(user_input: str):
    """The Agent will share the status of the DB instance provided by user"""

    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[connection_tool, queries_tool],
            messages=[
                {"role": "system", "content": "You are expert in handling the db instances"},
                {"role": "user", "content": user_input}
            ]
        )
        
        output = []

        tool_calls = response.choices[0].message.tool_calls

        if not tool_calls:
            return response.choices[0].message.content or "There are some error observred"
    
        else:
            for tool in tool_calls:
                func_name = tool.function.name
                arguments = json.loads(tool.function.arguments)

                if func_name in tool_dispatcher:
                    output.append(tool_dispatcher[func_name](**arguments))
                
                else:
                    output.append("Error has been observed while processing ")

            return "\n".join(output)
        
    except Exception as e:
        return f"The error has been encountered {e}"


if __name__ == "__main__":
    """The Agent retruns the db instance status"""

    user_input = "The inventory database is locking up. Check the active connections and get the slow queries for the 'prod-inventory-db' instance."

    print ("\n\n User Input: ",user_input)
    print("\n\n Agent is processing the information....")
    print ("\n\n Agent response: \n", llm_call(user_input))