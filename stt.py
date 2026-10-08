import os
import tempfile

import speech_recognition as sr


def speech_to_text(audio_file, language="en-US"):
   
    if audio_file is None:
        return None

    recognizer = sr.Recognizer()
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_file.getvalue())
            temp_path = tmp.name

        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)

        return recognizer.recognize_google(audio_data, language=language).strip()

    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print("Speech recognition service error:", e)
        return None
    except Exception as e:
        print("STT error:", e)
        return None
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
