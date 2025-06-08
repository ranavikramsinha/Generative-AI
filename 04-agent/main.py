from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import json
import requests
import os
import subprocess

load_dotenv()

client = OpenAI()

# def run_command(cmd: str):
#     result = os.system(cmd)
#     return result

def run_command(command: str):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()

# API call to get weather
def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return response.text

    return "Something went wrong! Please try again later."

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
}


SYSTEM_PROMPT = f"""
    You are an helpful AI assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning, select the relevant tools from the available tools and based on the tool selection you perform the action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    1. Follow the strict JSON output format.
    2. Always perform one step at a time and wait for the next input.
    3. Carefully analyse the user query.
    4. Don't answer the dangerous and illegal queries.

    Output JSON Format:
    {{ 
        "step": "string", 
        "content": "string", 
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function" 
    }}

    Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for that city.
    - "run_command": Takes linux command as a string and executes the command and returns the output after executing it.

    Examples:
    User: What is the weather in Bangalore?
    Output: {{ "step": "plan", "content": "The user is interested in weather data of banglore." }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather tool." }}
    Output: {{ "step": "action", "function": "get_weather", "input": "banglore" }}
    Output: {{ "step": "observe", "output":  "32 degrees Celsius" }}
    Output: {{ "step": "output", "content": "The weather for banglore is 32 degrees Celsius." }}
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

while True:
    query = input("👤: ")
    messages.append({"role": "user", "content": query})

    if(query == 'exit' or query == 'Exit'):
        break

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            response_format={"type": "json_object"},
            messages=messages
        )

        messages.append({"role": "assistant", "content": response.choices[0].message.content})

        parsed_response = json.loads(response.choices[0].message.content)

        if parsed_response.get("step") == "plan":
            print(f"🧠: {parsed_response.get('content')}")
            continue

        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print(f"⚙️: Calling tool: {tool_name} with input: {tool_input}")

            if available_tools.get(tool_name) != False:
                output = available_tools[tool_name](tool_input)
                messages.append({"role": "user", "content": json.dumps({ "step": "observe", "output": output})})
                continue

        if parsed_response.get("step") == "output":
            print(f"🤖: {parsed_response.get('content')}")
            break

# response = client.chat.completions.create(
#     model="gpt-4.1",
#     messages=[
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": "What is the weather in Banglore?"},
#         {"role": "assistant", "content": json.dumps({ "step": "plan", "content": "The user is interested in weather data of banglore." })},
#         {"role": "assistant", "content": json.dumps({"step": "plan", "content": "From the available tools I should call get_weather tool."})},
#         {"role": "assistant", "content": json.dumps({"step": "action", "function": "get_weather", "input": "banglore"})},
#         {"role": "assistant", "content": json.dumps({"step": "observe", "output": "32 degrees Celsius"})},
#         {"role": "assistant", "content": json.dumps({"step": "output", "content": "The weather for banglore is 32 degrees Celsius."})},
#     ],
# )

# print(f"🤖: {response.choices[0].message.content}")
