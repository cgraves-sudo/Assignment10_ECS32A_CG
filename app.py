import datetime
import json
import time
import uuid
from pathlib import Path

import requests
import streamlit as st

CHAT_DIRECTORY = Path("chats")
MEMORY_FILE = Path("memory.json")
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
    """Persist chat fields to JSON."""
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


def load_memory():
    """Load persisted user memory from disk."""
    if not MEMORY_FILE.exists():
        return {}

    try:
        memory = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    return memory if isinstance(memory, dict) else {}


def save_memory(memory_data):
    """Persist user memory as a JSON object."""
    MEMORY_FILE.write_text(json.dumps(memory_data, indent=2), encoding="utf-8")


def clear_memory():
    """Reset both session and file-backed memory while keeping the schema keys."""
    cleared_memory = {key: "" for key in st.session_state.memory.keys()}
    st.session_state.memory = cleared_memory
    save_memory(cleared_memory)


def ensure_memory_state():
    if "memory" not in st.session_state:
        st.session_state.memory = load_memory()


def merge_memory(existing_memory, new_memory):
    """Merge extracted one-word values into the existing schema."""
    if not isinstance(new_memory, dict):
        return existing_memory

    merged_memory = existing_memory.copy()
    for key in merged_memory.keys():
        value = new_memory.get(key, "")
        if isinstance(value, str):
            cleaned_value = value.strip().strip('"').strip("'")
            if cleaned_value:
                merged_memory[key] = cleaned_value
    return merged_memory


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
    """Update both the UI label and persisted chat title."""
    chat = st.session_state.chats.get(chat_id)
    if not chat:
        return

    cleaned_title = (generated_title or "").strip().strip('"').strip("'")
    if not cleaned_title:
        return

    final_title = cleaned_title[:30] + ("..." if len(cleaned_title) > 30 else "")
    chat["title"] = final_title
    chat["display_title"] = final_title


def should_generate_interface_title(chat):
    """Generate a title once, only for a newly started chat."""
    return chat.get("title", "New Chat") == "New Chat" and len(chat["messages"]) == 0


def extract_message_content(response_json):
    """Extract content from a standard non-streaming chat-completions response."""
    return response_json["choices"][0]["message"]["content"].strip()


def extract_stream_delta(chunk_json):
    """Extract incremental text content from a streamed chunk."""
    choices = chunk_json.get("choices", [])
    if not choices:
        return ""

    delta = choices[0].get("delta", {})
    content = delta.get("content", "")
    return content if isinstance(content, str) else ""


def stream_assistant_response(response):
    """Yield streamed assistant chunks from SSE data lines."""
    for raw_line in response.iter_lines(decode_unicode=True):
        if not raw_line:
            continue

        line = raw_line.strip()
        if not line.startswith("data:"):
            continue

        data = line[5:].strip()
        if not data or data == "[DONE]":
            continue

        try:
            chunk_json = json.loads(data)
        except json.JSONDecodeError:
            continue

        content = extract_stream_delta(chunk_json)
        if content:
            yield content
            time.sleep(0.03)


def build_title_payload(user_message):
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


def build_memory_payload(user_message, memory_schema):
    categories = ", ".join(memory_schema.keys())
    return {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return a valid JSON object only. "
                    f"Use exactly these keys: {categories}. "
                    "For each key, infer a one-word user preference or trait from the message. "
                    'If the message does not provide any suggestion for a category, return an empty string "". '
                    "Do not add extra keys. Do not include explanation."
                ),
            },
            {
                "role": "user",
                "content": user_message["content"],
            },
        ],
        "max_tokens": 150,
    }


def build_memory_system_message(memory_data):
    if not memory_data:
        return None

    filled_memory = {key: value for key, value in memory_data.items() if value not in ("", None, [], {})}
    if not filled_memory:
        return None

    return {
        "role": "system",
        "content": (
            "Use the following stored user memory to personalize tone and responses when relevant. "
            "Do not mention the memory explicitly unless it naturally helps the response.\n"
            f"User memory: {json.dumps(filled_memory)}"
        ),
    }


def parse_memory_response(response_json, memory_schema):
    """Parse the extracted memory response into the expected schema keys only."""
    memory_text = extract_message_content(response_json)
    parsed_memory = json.loads(memory_text)
    if not isinstance(parsed_memory, dict):
        return {}

    filtered_memory = {}
    for key in memory_schema.keys():
        value = parsed_memory.get(key, "")
        filtered_memory[key] = value if isinstance(value, str) else ""
    return filtered_memory


def recent_chat_row(chat):
    """Render one recent-chat row with open and delete controls."""
    is_active = chat["id"] == st.session_state.active_chat_id
    title_label = chat.get("display_title", chat["title"])

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


ensure_chat_state()
ensure_memory_state()
active_chat = st.session_state.chats[st.session_state.active_chat_id]
hf_token = st.secrets.get("HF_TOKEN", "")
if not hf_token:
    st.error("Missing HF_TOKEN in Streamlit secrets.")
    st.stop()

headers = {
    "Authorization": f"Bearer {hf_token}",
    "Content-Type": "application/json",
}

st.title("My AI Chat")

with st.sidebar:
    st.header("Chats")
    if st.button("New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    with st.expander("User Memory"):
        if st.button("Clear Memory", use_container_width=True, type="primary"):
            clear_memory()
            st.rerun()

        st.json(st.session_state.memory)

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

prompt = st.chat_input("Type a message and press Enter")

with st.container(height=700):
    for message in active_chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt:
        user_message = {"role": "user", "content": prompt}
        generated_title = None

        conversation_history = active_chat["messages"] + [user_message]
        payload_messages = []
        memory_system_message = build_memory_system_message(st.session_state.memory)
        if memory_system_message:
            payload_messages.append(memory_system_message)
        payload_messages.extend(conversation_history)

        payload = {
            "model": MODEL_NAME,
            "messages": payload_messages,
            "stream": True,
            "max_tokens": 512,
        }

        try:
            response = requests.post(
                CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload,
                stream=True,
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            st.error(f"API request failed: {exc}")
            st.stop()

        if should_generate_interface_title(active_chat):
            title_payload = build_title_payload(user_message)
            try:
                retrieve = requests.post(
                    CHAT_COMPLETIONS_URL,
                    headers=headers,
                    json=title_payload,
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
        save_chat(active_chat)

        with st.chat_message("assistant"):
            assistant_message = st.write_stream(stream_assistant_response(response))

        if not assistant_message:
            st.error("The API response did not contain any streamed assistant content.")
            st.stop()

        active_chat["messages"].append({"role": "assistant", "content": assistant_message})
        update_chat_title(active_chat["id"], generated_title)
        save_chat(active_chat)

        if st.session_state.memory:
            memory_payload = build_memory_payload(user_message, st.session_state.memory)
            try:
                memory_response = requests.post(
                    CHAT_COMPLETIONS_URL,
                    headers=headers,
                    json=memory_payload,
                    timeout=30,
                )
                memory_response.raise_for_status()
                memory_response_json = memory_response.json()
                extracted_memory = parse_memory_response(memory_response_json, st.session_state.memory)
                st.session_state.memory = merge_memory(st.session_state.memory, extracted_memory)
                save_memory(st.session_state.memory)
            except requests.exceptions.RequestException:
                pass
            except (ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError):
                pass

        st.rerun()
