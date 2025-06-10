# import streamlit as st
# from persona import client, SYSTEM_PROMPT

# # Initialize conversation history in session state
# if "messages" not in st.session_state:
#     st.session_state["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]

# # Configure the Streamlit app
# st.set_page_config(page_title="Chai aur Code Chat", layout="wide")

# # Header with custom styling
# IMAGE_URL = "https://images.pexels.com/photos/18264705/pexels-photo-18264705.jpeg"
# st.markdown(
#     f"""
#     <div style='text-align: center; margin-bottom: 20px;'>
#         <h2 style='display:inline-block; margin-left: 10px;'>Chai with Hitesh Sir ☕</h2>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# # Display conversation
# for msg in st.session_state["messages"]:
#     if msg["role"] == "user":
#         st.chat_message("user").write(msg["content"])
#     elif msg["role"] == "assistant":
#         st.chat_message("assistant", avatar=IMAGE_URL).write(msg["content"])

# # Input box for user
# user_input = st.chat_input("You:")
# if user_input:
#     # Append user message
#     st.session_state["messages"].append({"role": "user", "content": user_input})

#     # Call OpenAI API
#     with st.spinner("Hitesh Sir is typing..."):
#         response = client.chat.completions.create(
#             model="gpt-4.1-mini", messages=st.session_state["messages"]
#         )
#         assistant_message = response.choices[0].message.content

#     # Append assistant message and rerun
#     st.session_state["messages"].append({"role": "assistant", "content": assistant_message})
#     st.rerun()

import streamlit as st
from persona_copy import client, SYSTEM_PROMPT

# Configure Streamlit app (must be first Streamlit call)
st.set_page_config(page_title="Chai aur Code Chat", layout="wide")

# Initialize conversation history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]

# Header with custom styling
IMAGE_URL = "https://images.pexels.com/photos/18264705/pexels-photo-18264705.jpeg"
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='display:inline-block; margin-left: 10px;'>Chai with Hitesh Sir ☕</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# Display conversation history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant", avatar=IMAGE_URL).write(msg["content"])

# Chat input
user_input = st.chat_input("You:")
if user_input:
    # Append user message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Call OpenAI API
    with st.spinner("Hitesh Sir is typing..."):
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=st.session_state["messages"],
        )
    assistant_message = response.choices[0].message.content

    # Append assistant message and rerun to update UI
    st.session_state["messages"].append({"role": "assistant", "content": assistant_message})
    st.rerun()


# Note: Ensure `hitesh_persona.py` is in the same directory defining `client` and `SYSTEM_PROMPT`.

