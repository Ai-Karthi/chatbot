# TechNova AI Voice Assistant

Speech-to-speech HR assistant: you speak, it searches the TechNova handbook (RAG),
Qwen writes the answer, and the answer is shown as text **and** spoken back.
Chat history is stored in `chat_history.json`.

## Run
```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```
Linux only: `sudo apt install espeak-ng` (needed by pyttsx3).

## Files
| File | Purpose |
|---|---|
| app.py | Streamlit UI + pipeline |
| config.py | Settings (override via `.env`) |
| rag.py | Handbook chunking, embeddings, ChromaDB search |
| stt.py | Speech -> text |
| text_to_ai.py | Qwen model + prompt |
| tts.py | Text -> speech |
| memory.py | Conversation history (saved to JSON) |

Speech recognition uses Google's web API, so it needs internet.
