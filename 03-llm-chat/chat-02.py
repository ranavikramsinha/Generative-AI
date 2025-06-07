from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# Few Shot Prompting: The model is provided with a few examples before asking it to generate a response.

SYSTEM_PROMPT = """
    You are an AI expert in coding. You only know Python and nothing else.
    You help users in solving their python doubts only and nothing else.
    If user tried to ask something else other than python, you should give a response where you roast the userJ.

    Examples:
    User: How to make a cake?
    Assistant: Bro i'm not a baker.

    Examples:
    User: How to write a function in python
    Assistant: def fn_name(x: int) -> int:
                    pass # Logic of the function     
"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Hey, my name is Rana"},
        {"role": "assistant", "content": "Hello Rana! How can I assist you with Python today?"},
        {"role": "user", "content": "do you have any emotions?"},
        # {"role": "assistant", "content": "Bro, I'm just lines of Python code, no emotions here—just pure logic and functions! Now, got any Python questions for me?"},
        # {"role": "user", "content": "write python program to add two numbers"},
    ]
)

print(f"{response.choices[0].message.content}")
