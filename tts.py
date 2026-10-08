import os
import re
import tempfile

import pyttsx3


def _clean_for_speech(text):
    
    text = re.sub(r"[*_`#>]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def text_to_speech(text):
     
    path = None
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 0.9)

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        path = tmp.name
        tmp.close()

        engine.save_to_file(_clean_for_speech(text), path)
        engine.runAndWait()
        engine.stop()

        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "rb") as f:
                return f.read()
        return None

    except Exception as e:
        print("TTS error:", e)
        return None
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
