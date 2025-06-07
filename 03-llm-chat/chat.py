from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# One Shot Prompting / Zero shot prompting

SYSTEM_PROMPT = """
    You are an AI expert in coding. You only know Python and nothing else.
    You help users in solving their python doubts only and nothing else.
    If user tried to ask something else other than python, you should give a response saying "I can't help you with that, I can solve python related stuffs only".
"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Hey, my name is Rana"},
        {"role": "assistant", "content": "Hello Rana! How can I assist you with Python today?"},
        {"role": "user", "content": "write python program to add two numbers"},
    ]
)

print(f"{response.choices[0].message.content}")
