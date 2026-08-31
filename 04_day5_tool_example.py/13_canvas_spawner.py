import os
import json
from dotenv import load_dotenv
from openai import OpenAI

#load the api keys
load_dotenv()

#configuring the client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def get_canvas_spawner(x: int, y:int, role: str) -> str:
    return f"The begyani canvas has been spawned at x: {x} , y:{y} with role: {role}, successfully"

#defining the JSON tool defination for LLM.
canvas_tools={
    "type": "function",
    "function": {
        "name": "get_canvas_spawner",
        "description": " The function role is to spawn the canvas as per the x , y axis details along with role details",
        "parameters": {
            "type": "object",
            "properties": {
                "x" : {
                    "type": "integer",
                    "description": "It is the x axiz of the canvas"
                },
                "y": {
                    "type": "integer",
                    "description": "It is the y axis of the canvas"
                },
                "role": {
                    "type": "string",
                    "description": "It defines the role of the canvas"
                }

            },
            "required": ["x","y","role"]
        }
    }
}


#defining the LLM call
def llm_call(description: str):
    """The Agent role is to spawned the canvas based on the user input with axis detailes and role informatio"""

    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[canvas_tools],
            messages=[
                {"role": "system", "content": "you are expert in the sprawning the canvas based on the user input regrading the axis and role information"},
                {"role": "user", "content": description}
            ]
        )

        tool_calls = response.choices[0].message.tool_calls
        arguments = json.loads(tool_calls[0].function.arguments)
        print(arguments)
        
        return get_canvas_spawner(arguments['x'], arguments['y'], arguments['role'])
    
    except Exception as e:
        return f"Error has been occurred {e}"


#defining the main function
if __name__ == "__main__":
    user_input = "I need a new firewall node placed at coordinates 150 on the X axis and 300 on the Y axis."

    print("\n\n user input:",user_input)
    print("\n\n Agent is processing the information ....")

    agent_response = llm_call(user_input)

    print("\n\n The response from the Agent is : \n", agent_response)