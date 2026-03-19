import datetime
import json
import uuid
from pathlib import Path

import requests
import streamlit as st

json_data = {"name": "John Test", "age": 30}
CHAT_DIRECTORY = Path("chats")
CHAT_COMPLETIONS_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"


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
    stored_title = title or "New Chat"
    return {
        "id": chat_id or str(uuid.uuid4()),
        "title": stored_title,
        "display_title": stored_title,
        "created_at": timestamp,
        "messages": messages or [],
    }


def chat_file_path(chat_id):
    return CHAT_DIRECTORY / f"{chat_id}.json"


def save_chat(chat):
    """Persist only the JSON-backed chat fields."""
    CHAT_DIRECTORY.mkdir(exist_ok=True)
    persisted_chat = {
        "id": chat["id"],
        "title": chat["title"],
        "created_at": chat["created_at"],
        "messages": chat["messages"],
    }
    chat_file_path(chat["id"]).write_text(json.dumps(persisted_chat, indent=2), encoding="utf-8")


def delete_chat_file(chat_id):
    file_path = chat_file_path(chat_id)
    if file_path.exists():
        file_path.unlink()


def load_saved_chats():
    """Load valid chat JSON files from disk and restore display titles for the UI."""
    chats = {}
    CHAT_DIRECTORY.mkdir(exist_ok=True)

    for file_path in sorted(CHAT_DIRECTORY.glob("*.json")):
        try:
            chat = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        if not all(key in chat for key in ("id", "title", "created_at", "messages")):
            continue

        chat["display_title"] = chat.get("title", "New Chat")
        chats[chat["id"]] = chat

    return chats


def create_new_chat():
    """Create, store, and activate a fresh empty chat."""
    chat = build_chat()
    st.session_state.chats[chat["id"]] = chat
    st.session_state.active_chat_id = chat["id"]
    save_chat(chat)


def ensure_chat_state():
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


def update_chat_title(chat_id, generated_title):
    """Update the in-memory sidebar label only; do not persist it to disk."""
    chat = st.session_state.chats.get(chat_id)
    if not chat:
        return

    cleaned_title = (generated_title or "").strip().strip('"').strip("'")
    if not cleaned_title:
        return

    chat["display_title"] = cleaned_title[:30] + ("..." if len(cleaned_title) > 30 else "")


def should_generate_interface_title(chat):
    """Generate a title once, only for a newly started chat."""
    return chat.get("display_title", "New Chat") == "New Chat" and len(chat["messages"]) == 0


def extract_message_content(response_json):
    return response_json["choices"][0]["message"]["content"].strip()


def build_title_payload(user_message):
    """Ask the model for a short title-only label for the sidebar."""
    return {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Generate a short chat title of 5 words or fewer. "
                    "Return only the title, with no quotes and no explanation."
                ),
            },
            {
                "role": "user",
                "content": user_message["content"],
            },
        ],
        "max_tokens": 20,
    }


def recent_chat_row(chat):
    """Render one recent-chat row with open and delete controls."""
    is_active = chat["id"] == st.session_state.active_chat_id
    title_label = chat.get("display_title", chat["title"])

    title_column, date_column, delete_column = st.columns([4, 2, 1], gap="small")
    timestamp = format_timestamp(chat["created_at"])
    button_type = "primary" if is_active else "secondary"

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


ensure_chat_state()
active_chat = st.session_state.chats[st.session_state.active_chat_id]

st.title("My AI Chat")

with st.sidebar:
    st.header("Chats")
    if st.button("New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    with st.expander("User Memory"):
        st.button("Clear Memory", use_container_width=True, type="primary")
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

prompt = st.chat_input("Type a message and press Enter")

hf_token = st.secrets.get("HF_TOKEN", "")
if not hf_token:
    st.error("Missing HF_TOKEN in Streamlit secrets.")
    st.stop()

headers = {
    "Authorization": f"Bearer {hf_token}",
    "Content-Type": "application/json",
}

if prompt:
    user_message = {"role": "user", "content": prompt}
    conversation_history = active_chat["messages"] + [user_message]
    payload = {
        "model": MODEL_NAME,
        "messages": conversation_history,
        "max_tokens": 512,
    }

    try:
        response = requests.post(
            CHAT_COMPLETIONS_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        response_json = response.json()
        assistant_message = extract_message_content(response_json)
    except requests.exceptions.RequestException as exc:
        st.error(f"API request failed: {exc}")
        st.stop()
    except (ValueError, KeyError, IndexError, TypeError):
        st.error("The API response was not in the expected chat completion format.")
        st.stop()

    generated_title = None
    if should_generate_interface_title(active_chat):
        payload2 = build_title_payload(user_message)
        try:
            retrieve = requests.post(
                CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload2,
                timeout=30,
            )
            retrieve.raise_for_status()
            retrieve_json = retrieve.json()
            generated_title = extract_message_content(retrieve_json)
        except requests.exceptions.RequestException:
            generated_title = None
        except (ValueError, KeyError, IndexError, TypeError):
            generated_title = None

    active_chat["messages"].append(user_message)
    active_chat["messages"].append({"role": "assistant", "content": assistant_message})
    update_chat_title(active_chat["id"], generated_title)
    save_chat(active_chat)
    st.rerun()
