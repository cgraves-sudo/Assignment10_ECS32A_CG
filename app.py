import datetime
import json
import uuid
from pathlib import Path

import streamlit as st

json_data = {"name": "John Test", "age": 30}
CHAT_DIRECTORY = Path("chats")


st.set_page_config(page_title="My AI Chat", layout="wide")


def format_timestamp(iso_timestamp):
    """Convert an ISO timestamp into the short sidebar label format."""
    try:
        return datetime.datetime.fromisoformat(iso_timestamp).strftime("%b %d")
    except (TypeError, ValueError):
        return ""


def build_chat(title="New Chat", messages=None, created_at=None, chat_id=None):
    """Create the standard chat object used by session state and JSON files."""
    timestamp = created_at or datetime.datetime.now().isoformat()
    ##Here it makes a unique randomized ID for the chat_id variable, it also functions as the json file name
    return {
        "id": chat_id or str(uuid.uuid4()),
        "title": title,
        "created_at": timestamp,
        "messages": messages or [],
    }


def chat_file_path(chat_id):
    return CHAT_DIRECTORY / f"{chat_id}.json"


def save_chat(chat):
    CHAT_DIRECTORY.mkdir(exist_ok=True)
    chat_file_path(chat["id"]).write_text(json.dumps(chat, indent=2), encoding="utf-8")


def delete_chat_file(chat_id):
    file_path = chat_file_path(chat_id)
    if file_path.exists():
        file_path.unlink()


def load_saved_chats(): #Chat Dictionary Container for all chats generated
    """Load valid chat JSON files from disk."""
    chats = {}
    CHAT_DIRECTORY.mkdir(exist_ok=True)

    for file_path in sorted(CHAT_DIRECTORY.glob("*.json")):
        try:
            chat = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        if not all(key in chat for key in ("id", "title", "created_at", "messages")):
            continue

        chats[chat["id"]] = chat

    return chats


def create_new_chat():
    """Create, store, and activate a fresh empty chat."""
    chat = build_chat()
    st.session_state.chats[chat["id"]] = chat
    st.session_state.active_chat_id = chat["id"] # Identity of new chat stored in session state for active view
    save_chat(chat)


def ensure_chat_state(): # Verify Current Chat Line or Retrieves it -- This function checks if there are any existing chats in the session state. If not, it loads saved chats from disk. If there are still no chats after loading, it creates a new chat. It also ensures that the active chat ID is valid and points to an existing chat.
    """Initialize session state from saved chats or create a default chat."""
    if "chats" not in st.session_state:
        st.session_state.chats = load_saved_chats()

    if not st.session_state.chats:
        create_new_chat()
    elif (
        "active_chat_id" not in st.session_state
        or st.session_state.active_chat_id not in st.session_state.chats
    ):
        st.session_state.active_chat_id = next(iter(st.session_state.chats))


def set_active_chat(chat_id):
    if chat_id in st.session_state.chats:
        st.session_state.active_chat_id = chat_id


def choose_next_active_chat(deleted_chat_id):
    remaining_ids = [chat_id for chat_id in st.session_state.chats if chat_id != deleted_chat_id]
    return remaining_ids[0] if remaining_ids else None


def delete_chat(chat_id):
    """Delete a chat from session state and disk, then repair the active view."""
    was_active = st.session_state.active_chat_id == chat_id
    next_chat_id = choose_next_active_chat(chat_id)

    st.session_state.chats.pop(chat_id, None)
    delete_chat_file(chat_id)

    if not st.session_state.chats:
        create_new_chat()
        return

    if was_active or st.session_state.active_chat_id not in st.session_state.chats:
        st.session_state.active_chat_id = next_chat_id


def update_chat_title(chat_id): ### ADJUST THIS WHEN API INCORPORATION TO PROMPT AI TO COME UP WITH A TITLE PHRASE LESS THAN 30
    """Use the first user message as a stable, short sidebar title."""
    chat = st.session_state.chats[chat_id]
    if chat["title"] != "New Chat":
        return

    first_user_message = next(
        (message["content"] for message in chat["messages"] if message["role"] == "user"),
        "",
    ).strip()

    if first_user_message:
        chat["title"] = first_user_message[:30] + ("..." if len(first_user_message) > 30 else "")


def recent_chat_row(chat):
    """Render one recent-chat row with open and delete controls."""
    is_active = chat["id"] == st.session_state.active_chat_id
    title_label = chat["title"]
    if is_active:
        title_label = f"{title_label}"

    title_column, date_column, delete_column = st.columns([4, 2, 1], gap="small")
    timestamp = format_timestamp(chat["created_at"])
    button_type = "secondary" if is_active else "tertiary"

    with title_column:
        if st.button(
            title_label,
            key=f"open_chat_{chat['id']}",
            use_container_width=True,
            type=button_type,
        ):
            set_active_chat(chat["id"])
            st.rerun()

    with date_column:
        st.caption(timestamp)

    with delete_column:
        if st.button("X", key=f"delete_chat_{chat['id']}", type="primary"):
            delete_chat(chat["id"])
            st.rerun()


## Main app logic starts here:

ensure_chat_state()
active_chat = st.session_state.chats[st.session_state.active_chat_id] # List Type Container for active content

st.title("My AI Chat")

with st.sidebar:
    st.header("Chats")
    if st.button("New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    with st.expander("User Memory"):
        st.button("Clear Memory", use_container_width=True,
            type="primary")
        st.write("This is where user memory will be displayed.")
        for key, value in json_data.items():
            with st.popover(f"{key}"):
                st.write(value)

    st.write("")
    st.divider()
    st.write("Recent Chats")

    chats_sorted = sorted(
        st.session_state.chats.values(),
        key=lambda chat: chat["created_at"],
        reverse=True,
    )
    for chat in chats_sorted:
        recent_chat_row(chat)

with st.container(height=500):
    for message in active_chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

##load context :: SEND THE FULL MESSAGE HISTORY with each API request so the model maintains context.

prompt = st.chat_input("Type a message and press Enter")

if prompt: ## History Appends and Interface
    active_chat["messages"].append({"role": "user", "content": prompt}) # User Input Append
    response = f"Echo: {prompt}"
    active_chat["messages"].append({"role": "assistant", "content": response}) # Bot Output Append

    update_chat_title(active_chat["id"])
    save_chat(active_chat) # Json dump to chat file path
    st.rerun()
