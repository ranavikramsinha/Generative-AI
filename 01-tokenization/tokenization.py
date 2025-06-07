import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o")

text = input(f"Enter English text to tokenize: ")
tokens = encoder.encode(text)
print(f"Tokens: {tokens}")

tokens = [int(t) for t in tokens]
text = encoder.decode(tokens)

print(f"Text: {text}")