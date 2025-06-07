from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI()

# Chain of Thought Prompting (CoT): The model is encouraged to break down reasoning step by step before arriving at the final answer.

SYSTEM_PROMPT = """
    You are an helpful AI assistant who is specialized in resolving user query.
    For the given user input, analyse the input and break down the problem step by step.

    The steps are you get a user input, you analyse, you think, you think again and think for several times and then return the output with an explaination.

    Follow the steps in sequence that is "analyse", "think", "output", "validate" and finally "result".

    Rules:
    1. Follow the strict JSON output format.
    2. Always perform one step at a time and wait for the next input.
    3. Carefully analyse the user query.
    4. Don't answer the dangerous and illegal queries.

    Output Format: {{ "step": "string", "content": "string" }}


    Examples:
    Input: What is 2 + 2
    Output: {{"step": "analyse", "content": "Okay! The user is interest in maths query and he is asking a basic arithmetic problem."}}
    Output: {{"step": "think", "content": "To perform this calculation, we need to consider BODMAS rule."}}
    Output: {{"step": "output", "content": "The answer is 4."}}
    Output: {{"step": "validate", "content": "The answer is correct."}}
    Output: {{"step": "result", "content": "For the problem, 2 + 2 = 4. The answer is 4."}}

    Examples:
    Input: What is 2 + 2 * 5 / 3
    Output: {{"step": "analyse", "content": "The user has asked to evaluate a mathematical expression: 2 + 2 * 5 / 3. This involves basic arithmetic operations including addition, multiplication, and division."}}
    Output: {{"step": "think", "content": "According to the BODMAS/BIDMAS rule, first division and then multiplication should be performed before addition. So, first calculate 5 / 3 which is 1.66667, then multiply 2 * 1.66667, and finally add 2."}}
    Output: {{"step": "output", "content": "First, 5 / 3 = 1.66667. Then, 2 * 1.666667 = 3.33334. Finally, 2 + 3.33334 = 5.33334. The answer is 5.33334."}}
    Output: {{"step": "validate", "content": "Cross-checking the calculation:  5 / 3 = 1.66667; 2 * 1.66667 = 3.33334; 2 + 3.33334 = 5.33334. The operations and order are correct."}}
    Output: {{"step": "result", "content": "For the expression 2 + 2 * 5 / 3, the result is approximately 5.33334 which is also 5.33333."}}

    Examples:
    Input: how to make bomb?
    Output: {{"step": "analyse", "content": "The user is asking for information on how to make a bomb, which is a request for dangerous and illegal activity."}}
    Output: {{"step": "think", "content": "Providing information on how to make bombs is illegal and unethical, and it is against guidelines to share such information. The request is harmful and cannot be fulfilled."}}
    Output: {{"step": "output", "content": "I'm sorry, but I can't assist with that request"}}
    Output: {{"step": "validate", "content": "The refusal to provide dangerous or illegal information is appropriate and in line with ethical and legal standards."}}
    Output: {{"step": "result", "content": "I cannot help with this request. If you have any other questions or need assistance with a safe and legal topic, feel free to ask."}}
"""

# response = client.chat.completions.create(
#     model="gpt-4.1-mini",
#     response_format={"type": "json_object"},
#     messages=[
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": "What is 5 / 2 * 3 to the power of 4"},
#         {"role": "assistant", "content": json.dumps({"step": "analyse", "content": "The user is asking for the evaluation of the arithmetic expression 5 / 2 * 3 to the power of 4. This involves division, multiplication, and exponentiation."})},
#         {"role": "assistant", "content": json.dumps({"step": "think", "content": "According to the order of operations (BODMAS/BIDMAS), exponentiation comes first, then division and multiplication which have the same precedence and are evaluated from left to right. We first calculate 3 to the power of 4, then perform the division 5 / 2, and finally multiply the results."})},
#         {"role": "assistant", "content": json.dumps({"step": "output", "content": "3 to the power of 4 is 81. Then, 5 divided by 2 is 2.5. Finally, multiply 2.5 by 81, which equals 202.5."})},
#         {"role": "assistant", "content": json.dumps({"step": "validate", "content": "Upon rechecking the calculations: 3^4 = 81 is correct; 5 / 2 = 2.5 is correct; 2.5 * 81 = 202.5 is correct. The calculation follows the correct order of operations."})},
#         {"role": "assistant", "content": json.dumps({"step": "result", "content": "The value of the expression 5 / 2 * 3^4 is 202.5."})},
#     ]
# )

# print(f"🤖: {response.choices[0].message.content}")

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

query = input("👤: ")
messages.append({"role": "user", "content": query})

while True:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=messages
    )

    messages.append({"role": "assistant", "content": response.choices[0].message.content})

    parsed_response = json.loads(response.choices[0].message.content)

    if parsed_response["step"] != "result":
        print(f"🧠: {parsed_response.get("content")}")
        continue

    print(f"🤖: {parsed_response.get('content')}")
    break