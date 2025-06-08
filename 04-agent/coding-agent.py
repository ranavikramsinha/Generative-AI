import os
import json
import textwrap
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

def run_command(command: str):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()

def add(x, y):
    print(f"⛏️: Tool Called: add", x, y)
    return x + y

def create_file(params):
    print(f"⛏️: Tool Called: create_file {params}")

    try:
        data = json.loads(params) if isinstance(params, str) else params
        filename = data.get("filename")
        content = data.get("content", "")

        os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"{filename} created successfully"
    
    except Exception as e:
        return f"Error creating file: {e}"

def edit_file(params):
    print(f"⛏️: Tool Called: edit_file {params}")
    try:
        data = json.loads(params) if isinstance(params, str) else params
        filename = data.get("filename")
        content = data.get("content", "")

        mode = data.get("mode", "w")  # 'w' replace or 'a' append

        with open(filename, mode, encoding="utf-8") as f:
            f.write(content)
        return f"{filename} edited successfully"
    
    except Exception as e:
        return f"Error editing file: {e}"

def create_sum_file(params=None):
    print(f"⛏️: Tool Called: create_sum_file {params}")

    template = textwrap.dedent('''\
        def add(x, y):
            """Return the sum of two numbers."""
            return x + y

        if __name__ == "__main__":
            a = int(input("Enter first number: "))
            b = int(input("Enter second number: "))
            print("Sum:", add(a, b))
    ''')

    with open("sum.py", "w", encoding="utf-8") as f:
        f.write(template)
    return "sum.py created successfully"

def git_commit_and_push(params):
    print(f"⛏️: Tool Called: git_commit_and_push {params}")
    try:
        data = json.loads(params) if isinstance(params, str) else params
        message = data.get("message", "")
        out_add = run_command("git add .")
        out_commit = run_command(f'git commit -m "{message}"')
        out_push = run_command("git push")

        return f"git add output:\n{out_add}\ngit commit output:\n{out_commit}\ngit push output:\n{out_push}"
    
    except Exception as e:
        return f"Error in git_commit_and_push: {e}"

available_tools = {
    "add": {"function": add},
    "run_command": {"function": run_command},
    "create_file": {"function": create_file},
    "edit_file": {"function": edit_file},
    "create_sum_file": {"function": create_sum_file},
    "git_commit_and_push": {"function": git_commit_and_push}
}

SYSTEM_PROMPT = """
You are an AI assistant that plans steps and uses tools to fulfill user requests.
Follow start, analyse, action, observe, output flow with JSON steps.

Output JSON format:
{
  "step": <plan|action|observe|output>,
  "content": "string",
  "function": "tool_name if action",
  "input": "parameters"
}

Available tools:
- create_file
- edit_file
- create_sum_file
- run_command
- add
- git_commit_and_push

Examples:
1) Create any file:
  plan: use create_file
  action: create_file, input: {"filename":"example.txt","content":"Hello"}
  observe: example.txt created successfully
  output: "Created example.txt with provided content."

2) Run code files:
  plan: use run_file
  action: run_file, input: {"filename":"script.cpp"}
  observe: <compile/run output>
  output: "Here's the output of script.cpp."

3) Push to GitHub:
  plan: use git_commit_and_push
  action: git_commit_and_push, input: {"message":"Commit message"}
  observe: <git outputs>
  output: "All changes committed and pushed!"
"""

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

while True:
    query = input("👤: ")
    messages.append({"role": "user", "content": query})

    if query.strip().lower() in ["exit", "quit"]:
        print("Exiting. Goodbye!")
        break
    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14", messages=messages
        )

        parsed = json.loads(response.choices[0].message.content)

        messages.append({"role":"assistant","content":json.dumps(parsed)})

        if parsed["step"] == "plan":
            print(f"🧠: {parsed['content']}")
            continue

        if parsed["step"] == "action":
            tool, inp = parsed["function"], parsed.get("input", "")

            if tool in available_tools:
                output = available_tools[tool]["function"](inp)
                messages.append({"role":"assistant","content":json.dumps({"step":"observe","output":output})})
                continue

        if parsed["step"] == "output":
            print(f"🤖: {parsed['content']}")
            break
