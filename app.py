# Windows PowerShell Activated
# Installed Required Packages
# Streamlit Application Running in PY

import datetime
import streamlit as st

json_data = {"name": "John Test", "age": 30}

# Page Set Up
st.set_page_config(page_title="My AI Chat", layout="wide")

# Functionalities

def recent_chats(title, timestamp):
    """Placeholder function for recent chats.
    In a real application, this would fetch and display recent chat history."""
    """Add a button for each new chat
    Button function to open the corresponding chat
    Add a timestamp (Mon DD)
    In the same row, place an X button that functions to delete the corresponding chat and button"""


st.title("My AI Chat")

# Crafting sidebar for chats, user memory, and recent chats
with st.sidebar:
    st.header("Chats")
    st.button("New Chat")
    with st.expander("User Memory"):
        st.button("Clear Memory")
        ## Placeholder for user memory JSON data
        st.write("This is where user memory will be displayed.")
        for key in json_data.keys():
            with st.popover(f"{key}"):
                st.write(json_data[key])
    st.space("large")
    st.divider()
    st.write("Recent Chats")
    # Placeholder for Loop for recent_chats function for each new chat and corresponding button
    st.button("Placeholder for Chat 1")
    recent_chats("Chat 1", datetime.datetime.now().strftime("%b %d"))

# UI for chat interface, displaying messages, and accepting user input
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history in a fixed-height scrollable container.
with st.container(height=500):
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

prompt = st.chat_input("Type a message and press Enter")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Echo: {prompt}"  # Placeholder for AI response generation logic
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Show the newest messages immediately on the rerun triggered by chat_input.
    st.rerun()



