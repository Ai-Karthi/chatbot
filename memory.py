import json
import os
import streamlit as st

from config import HISTORY_PATH, HISTORY_WINDOW

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are the TechNova Solutions AI HR and career assistant.\n\n"
        "Answer questions using ONLY the provided TechNova employee handbook "
        "context.\n\n"
        "Rules:\n"
        "1. Do not invent information.\n"
        "2. Do not guess.\n"
        "3. Do not use outside knowledge.\n"
        "4. If the answer is not in the handbook, say that the information is "
        "not available in the TechNova handbook.\n"
        "5. Keep answers concise and suitable for speech."),}


def _load_saved():
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return [
            m for m in data
            if m.get("role") in ("user", "assistant") and m.get("content")]
        
    except Exception:
        return []


def _save():
    try:
        messages = [
            m for m in st.session_state.conversation_history
            if m["role"] != "system" ]
        
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            
            json.dump(messages, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print("Could not save history:", e)


def initialize_memory():
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = (
            [SYSTEM_MESSAGE.copy()] + _load_saved() )


def add_user_message(text):
    initialize_memory()
    st.session_state.conversation_history.append(
        {"role": "user", "content": text})
    _save()


def add_ai_message(text):
    initialize_memory()
    st.session_state.conversation_history.append(
        {"role": "assistant", "content": text})
    _save()


def get_conversation_history():
    initialize_memory()
    return st.session_state.conversation_history


def get_recent_history(window=HISTORY_WINDOW):
    
    history = get_conversation_history()
    chat = [m for m in history if m["role"] != "system"]
    return [SYSTEM_MESSAGE.copy()] + chat[-window:]


def clear_memory():
    st.session_state.conversation_history = [SYSTEM_MESSAGE.copy()]
    st.session_state.audio_store = {}
    if os.path.exists(HISTORY_PATH):
        os.remove(HISTORY_PATH)
