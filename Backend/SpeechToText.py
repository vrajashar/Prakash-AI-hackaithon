import speech_recognition as sr
import nltk

nltk.download('punkt')

def QueryModifier(query):
    """Formats the query to ensure proper punctuation."""
    query = query.strip().capitalize()
    if not query.endswith(("?", ".", "!")):
        query += "."
    return query

def SpeechRecognition():
    """Captures speech from the microphone and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Speak now.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)  # No timeout, keeps listening
            text = recognizer.recognize_google(audio)
            return QueryModifier(text)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."
        except sr.RequestError:
            return "Could not request results, please check your connection."
        except sr.WaitTimeoutError:
            return "Listening timed out. Please try again."

if __name__ == "__main__":
    while True:
        detected_text = SpeechRecognition()
        print(detected_text)
