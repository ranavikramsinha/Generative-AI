import os
import json
import textwrap
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

def run_command(command: str):
    """Execute a shell command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()

def add(x, y):
    """Add two numbers."""
    print(f"⛏️: Tool Called: add({x}, {y})")
    return x + y

def create_file(params):
    """Create a new file with specified content."""
    print(f"⛏️: Tool Called: create_file {params}")

    try:
        data = json.loads(params) if isinstance(params, str) else params
        filename = data.get("filename")
        content = data.get("content", "")

        if not filename:
            return "Error: filename is required"

        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ {filename} created successfully"
    
    except Exception as e:
        return f"❌ Error creating file: {e}"

def edit_file(params):
    """Edit an existing file or create if it doesn't exist."""
    print(f"⛏️: Tool Called: edit_file {params}")
    try:
        data = json.loads(params) if isinstance(params, str) else params
        filename = data.get("filename")
        content = data.get("content", "")
        mode = data.get("mode", "w")  # 'w' replace, 'a' append

        if not filename:
            return "Error: filename is required"

        with open(filename, mode, encoding="utf-8") as f:
            f.write(content)
        return f"✅ {filename} edited successfully"
    
    except Exception as e:
        return f"❌ Error editing file: {e}"

def create_sum_file(params=None):
    """Create a simple sum.py file with addition functionality."""
    print(f"⛏️: Tool Called: create_sum_file")

    template = textwrap.dedent('''\
        def add(x, y):
            """Return the sum of two numbers."""
            return x + y

        if __name__ == "__main__":
            try:
                a = int(input("Enter first number: "))
                b = int(input("Enter second number: "))
                print(f"Sum: {add(a, b)}")
            except ValueError:
                print("Please enter valid numbers")
    ''')

    try:
        with open("sum.py", "w", encoding="utf-8") as f:
            f.write(template)
        return "✅ sum.py created successfully"
    except Exception as e:
        return f"❌ Error creating sum.py: {e}"

def git_commit_and_push(params):
    """Add, commit, and push changes to git repository."""
    print(f"⛏️: Tool Called: git_commit_and_push {params}")
    try:
        data = json.loads(params) if isinstance(params, str) else params
        message = data.get("message", "Auto-commit")
        
        if not message.strip():
            return "❌ Error: commit message cannot be empty"

        out_add = run_command("git add .")
        out_commit = run_command(f'git commit -m "{message}"')
        out_push = run_command("git push")

        return f"✅ Git operations completed:\n📁 Add: {out_add or 'No output'}\n💾 Commit: {out_commit}\n🚀 Push: {out_push}"
    
    except Exception as e:
        return f"❌ Error in git operations: {e}"

available_tools = {
    "add": {
        "function": add,
        "description": "Add two numbers together",
        "params": "Pass two numbers as parameters"
    },
    "run_command": {
        "function": run_command,
        "description": "Execute shell commands",
        "params": "Pass command as string"
    },
    "create_file": {
        "function": create_file,
        "description": "Create a new file with content",
        "params": '{"filename": "path/to/file", "content": "file content"}'
    },
    "edit_file": {
        "function": edit_file,
        "description": "Edit or append to existing file",
        "params": '{"filename": "path/to/file", "content": "new content", "mode": "w|a"}'
    },
    "create_sum_file": {
        "function": create_sum_file,
        "description": "Create a simple Python addition script",
        "params": "No parameters required"
    },
    "git_commit_and_push": {
        "function": git_commit_and_push,
        "description": "Git add, commit, and push changes",
        "params": '{"message": "commit message"}'
    }
}

SYSTEM_PROMPT = """
You are an AI assistant that helps users by planning and executing tasks using available tools.

WORKFLOW: You must follow this exact 4-step process:
1. **PLAN** - Analyze the request and decide which tools to use
2. **ACTION** - Execute the chosen tool with proper parameters  
3. **OBSERVE** - Process the tool's output/result
4. **OUTPUT** - Provide final response to the user

RESPONSE FORMAT: Always respond with valid JSON in this exact structure:
{
  "step": "plan|action|observe|output",
  "content": "description of what you're doing",
  "function": "tool_name (only for action step)",
  "input": "tool parameters (only for action step)"
}

AVAILABLE TOOLS:
- **create_file**: Create new files with content
  Input: {"filename": "path/file.ext", "content": "file content"}
  
- **edit_file**: Edit existing files (replace or append)
  Input: {"filename": "path/file.ext", "content": "new content", "mode": "w|a"}
  
- **create_sum_file**: Create a simple Python addition script
  Input: No parameters needed
  
- **run_command**: Execute shell commands  
  Input: "command string"
  
- **add**: Add two numbers
  Input: Pass two numbers as parameters
  
- **git_commit_and_push**: Git add, commit and push changes
  Input: {"message": "commit message"}

EXAMPLES:

Example 1 - Creating a file:
Step 1: {"step": "plan", "content": "User wants to create a file. I'll use create_file tool."}
Step 2: {"step": "action", "function": "create_file", "input": {"filename": "hello.txt", "content": "Hello World"}}
Step 3: {"step": "observe", "content": "File created successfully"}  
Step 4: {"step": "output", "content": "I've created hello.txt with the content 'Hello World'."}

Example 2 - Running a command:
Step 1: {"step": "plan", "content": "User wants to run a Python file. I'll use run_command."}
Step 2: {"step": "action", "function": "run_command", "input": "python script.py"}
Step 3: {"step": "observe", "content": "Command executed, output: [command output]"}
Step 4: {"step": "output", "content": "Here's the output from running script.py: [results]"}

IMPORTANT RULES:
- Always follow the 4-step workflow in order
- Each step must be a separate JSON response
- Only include "function" and "input" fields in action steps
- Be specific and helpful in your content descriptions
- Handle errors gracefully and inform the user
"""

def main():
    """Main conversation loop."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    print("🤖 AI Agent Ready! Type 'exit' or 'quit' to stop.")
    print("=" * 50)
    
    while True:
        try:
            query = input("\n👤 You: ").strip()
            
            if query.lower() in ["exit", "quit", "bye"]:
                print("👋 Goodbye!")
                break
                
            if not query:
                continue
                
            messages.append({"role": "user", "content": query})
            
            # Process the request through the workflow
            while True:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    response_format={"type": "json_object"},
                    messages=messages,
                )
                
                try:
                    parsed = json.loads(response.choices[0].message.content)
                    messages.append({"role": "assistant", "content": json.dumps(parsed)})
                    
                    step = parsed.get("step")
                    content = parsed.get("content", "")
                    
                    if step == "plan":
                        print(f"🧠 Planning: {content}")
                        
                    elif step == "action":
                        tool_name = parsed.get("function")
                        tool_input = parsed.get("input", "")
                        
                        print(f"⚡ Action: Using {tool_name}")
                        
                        if tool_name in available_tools:
                            try:
                                output = available_tools[tool_name]["function"](tool_input)
                                observe_msg = {"step": "observe", "content": f"Tool result: {output}"}
                                messages.append({"role": "assistant", "content": json.dumps(observe_msg)})
                            except Exception as e:
                                error_msg = {"step": "observe", "content": f"Tool error: {str(e)}"}
                                messages.append({"role": "assistant", "content": json.dumps(error_msg)})
                        else:
                            error_msg = {"step": "observe", "content": f"Error: Tool '{tool_name}' not found"}
                            messages.append({"role": "assistant", "content": json.dumps(error_msg)})
                            
                    elif step == "observe":
                        print(f"👁️  Observing: {content}")
                        
                    elif step == "output":
                        print(f"🤖 Result: {content}")
                        break
                        
                    else:
                        print(f"❓ Unknown step: {step}")
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"Raw response: {response.choices[0].message.content}")
                    break
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()