import hashlib
import os
import streamlit as st

from config import APP_NAME, TOP_K, WELCOME_AUDIO
from memory import (
    initialize_memory,
    add_user_message,
    add_ai_message,
    get_conversation_history,
    get_recent_history,
    clear_memory,)



st.set_page_config(page_title="TechNova AI Assistant", page_icon="🤖", layout="wide")


with st.spinner("Loading models (first run can take a few minutes)..."):
    
    from stt import speech_to_text
    from text_to_ai import get_ai_response, build_prompt
    from tts import text_to_speech
    from rag import retrieve_information, ensure_database


initialize_memory()

st.session_state.setdefault("audio_store", {})      
st.session_state.setdefault("autoplay_index", None)  
st.session_state.setdefault("last_audio_hash", None) 
st.session_state.setdefault("audio_key", 0)          
st.session_state.setdefault("notice", None)         

if "db_ready" not in st.session_state:
    with st.spinner("Loading TechNova knowledge base..."):
        try:
            st.session_state.chunk_count = ensure_database()
            st.session_state.db_ready = True
        except Exception as e:
            st.session_state.db_ready = False
            st.session_state.db_error = str(e)


def answer_question(question, speak=True):
   
    history = get_recent_history()

    with st.spinner("Searching TechNova knowledge base..."):
        chunks = retrieve_information(question, top_k=TOP_K)
        
    context = "\n\n".join(chunks) if chunks else "No relevant information was found."

    with st.spinner("Generating answer..."):
        answer = get_ai_response(history, build_prompt(context, question))

    add_user_message(question)
    add_ai_message(answer)
    index = len(get_conversation_history()) - 1

    if speak:
        with st.spinner("Generating voice..."):
            audio_bytes = text_to_speech(answer)
            
        if audio_bytes:
            st.session_state.audio_store[index] = audio_bytes
            st.session_state.autoplay_index = index
        else:
            st.session_state.notice = ("warning", "Voice could not be generated; showing text only.")



st.title(f"🤖 {APP_NAME}")
st.caption("Speech-to-Speech • Qwen • RAG • ChromaDB")


with st.sidebar:
    st.header("⚙️ System Status")

    if st.session_state.get("db_ready"):
        st.success("ChromaDB: Connected")
        st.info(f"Knowledge chunks: {st.session_state.chunk_count}")
    else:
        st.error("ChromaDB: Error")
        st.caption(st.session_state.get("db_error", ""))

    st.divider()
    st.header("🎛️ Controls")

    speak_enabled = st.toggle("🔊 Speak answers", value=True)

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        clear_memory()
        st.rerun()

    if os.path.exists(WELCOME_AUDIO):
        st.caption("Welcome message")
        st.audio(WELCOME_AUDIO)

    st.divider()
    st.markdown(
        """
        **Knowledge Base:** TechNova Solutions Employee Handbook

        **Model:** Qwen 2.5 1.5B Instruct

        **Vector DB:** ChromaDB

        **Embedding:** all-MiniLM-L6-v2

        **STT:** Google Speech Recognition

        **TTS:** pyttsx3
        """ )


history = get_conversation_history()

if len(history) == 1:
    st.info("👋 Press the microphone below and ask a question about TechNova policies.")

for i, message in enumerate(history):
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message["role"] == "assistant" and i in st.session_state.audio_store:
            st.audio(
                st.session_state.audio_store[i],
                format="audio/wav",
                autoplay=(i == st.session_state.autoplay_index), )


st.session_state.autoplay_index = None

if st.session_state.notice:
    kind, text = st.session_state.notice
    getattr(st, kind)(text)
    st.session_state.notice = None


st.divider()
st.subheader("🎤 Ask by Voice")

audio_file = st.audio_input(
    "Press the microphone, ask your question, then press stop",
    key=f"audio_input_{st.session_state.audio_key}", )

if audio_file is not None:
    audio_hash = hashlib.md5(audio_file.getvalue()).hexdigest()

    if audio_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = audio_hash

        with st.spinner("Converting speech to text..."):
            user_text = speech_to_text(audio_file)

        if not user_text:
            st.session_state.notice = (
                "warning",
                "I could not understand your speech. Please try again "
                "(speech recognition needs an internet connection).",)
        else:
            answer_question(user_text, speak=speak_enabled)

        st.session_state.audio_key += 1 
        st.rerun()


user_question = st.chat_input("Or type your question about TechNova policies...")

if user_question:
    answer_question(user_question, speak=speak_enabled)
    st.rerun()
