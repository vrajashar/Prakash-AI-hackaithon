from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

env_vars = dotenv_values(".env")

InputLanguage = env_vars.get("InputLanguage")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''


HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

with open(r"Data/Voice.html", "w") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()

Link = f"{current_dir}/Data/Voice.html"

chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Allow microphone use
chrome_options.add_argument("--use-fake-device-for-media-stream")  # Simulate microphone
chrome_options.add_argument("--disable-features=MediaCapture")  # Disable video capture
chrome_options.add_argument("--disable-features=UseCamera")  # Prevent camera usage
chrome_options.add_argument("--disable-webrtc-hw-encoding")  # Disable WebRTC video encoding
chrome_options.add_argument("--disable-webrtc-hw-decoding")  # Disable WebRTC video decoding
chrome_options.add_argument("--disable-webrtc-encryption")  # Disable WebRTC encryption
chrome_options.add_argument("--disable-gpu")  # Avoid GPU-related issues
chrome_options.add_argument("--disable-software-rasterizer")  # Prevent software rendering issues
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
chrome_options.add_argument("--disable-dev-shm-usage")  # Helps with resource allocation
chrome_options.add_argument("--allow-file-access-from-files")
chrome_options.add_argument("--allow-file-access")
chrome_options.add_argument("--disable-web-security")



CHROMEDRIVER_PATH = r"C:\Users\ASUS\Desktop\AI\jarvis\Backend\chromedriver.exe"
service = Service(CHROMEDRIVER_PATH)

driver = webdriver.Chrome(service=service, options=chrome_options)

TempDirPath = rf"{current_dir}/Frontend/Files"

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question.
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Function to translate text into English using the mtranslate library.
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    driver.get("file:///" + Link)
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            # Get the recognized text from the HTML output element.
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                # Stop recognition by clicking the stop button.
                driver.find_element(by=By.ID, value="end").click()

                # If the input language is English, return the modified query.
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    # If the input language is not English, translate the text and return it.
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))

        except Exception as e:
            pass

if __name__ == "__main__":
    while True:
        # Continuously perform speech recognition and print the recognized text.
        Text = SpeechRecognition()
        print(Text)

        

# import speech_recognition as sr
# import mtranslate as mt
# from dotenv import dotenv_values

# # Load environment variables
# env_vars = dotenv_values(".env")
# InputLanguage = env_vars.get("InputLanguage", "en")  # Default to English if not set

# # Function to adjust query punctuation and formatting
# def QueryModifier(Query):
#     new_query = Query.lower().strip()
#     query_words = new_query.split()
#     question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

#     if any(word + " " in new_query for word in question_words):
#         if query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + "?"
#         else:
#             new_query += "?"
#     else:
#         if query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + "."
#         else:
#             new_query += "."

#     return new_query.capitalize()

# # Function to translate text to English if needed
# def UniversalTranslator(Text):
#     return mt.translate(Text, "en").capitalize()

# # Speech recognition function
# def SpeechRecognition():
#     recognizer = sr.Recognizer()
#     recognizer.energy_threshold = 300  # Adjust microphone sensitivity
#     recognizer.dynamic_energy_threshold = True  # Auto-adjust based on background noise

#     with sr.Microphone() as source:
#         print("🔊 Listening... Speak now!")

#         # Adjust for background noise
#         recognizer.adjust_for_ambient_noise(source, duration=1)

#         try:
#             # Capture audio with timeout
#             audio = recognizer.listen(source, timeout=15, phrase_time_limit=10)
#             print("🎤 Processing...")

#             # Recognize speech
#             detected_text = recognizer.recognize_google(audio, language=InputLanguage)

#             if not detected_text:
#                 print("❌ No speech detected. Try again.")
#                 return ""

#             # Translate if needed
#             if "en" not in InputLanguage.lower():
#                 print("🌎 Translating to English...")
#                 detected_text = UniversalTranslator(detected_text)

#             # Format the query
#             return QueryModifier(detected_text)

#         except sr.WaitTimeoutError:
#             print("⏳ No speech detected within time limit.")
#             return ""

#         except sr.UnknownValueError:
#             print("🤔 Could not understand audio.")
#             return ""

#         except sr.RequestError:
#             print("⚠️ Speech recognition service is unavailable.")
#             return ""

# # Continuous recognition loop
# if __name__ == "__main__":
#     while True:
#         text = SpeechRecognition()
#         if text:
#             print(f"✅ Recognized: {text}")


# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from dotenv import dotenv_values
# import os
# import spacy
# import mtranslate as mt

# # Load NLP model
# nlp = spacy.load("en_core_web_sm")

# env_vars = dotenv_values(".env")
# InputLanguage = env_vars.get("InputLanguage")

# HtmlCode = '''<!DOCTYPE html>
# <html lang="en">
# <head>
#     <title>Speech Recognition</title>
# </head>
# <body>
#     <button id="start" onclick="startRecognition()">Start Recognition</button>
#     <button id="end" onclick="stopRecognition()">Stop Recognition</button>
#     <p id="output"></p>
#     <script>
#         const output = document.getElementById('output');
#         let recognition;

#         function startRecognition() {
#             recognition = new webkitSpeechRecognition() || new SpeechRecognition();
#             recognition.lang = '';
#             recognition.continuous = true;

#             recognition.onresult = function(event) {
#                 const transcript = event.results[event.results.length - 1][0].transcript;
#                 output.textContent += transcript;
#             };

#             recognition.onend = function() {
#                 recognition.start();
#             };
#             recognition.start();
#         }

#         function stopRecognition() {
#             recognition.stop();
#             output.innerHTML = "";
#         }
#     </script>
# </body>
# </html>'''

# HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# with open(r"Data/Voice.html", "w") as f:
#     f.write(HtmlCode)

# current_dir = os.getcwd()
# Link = f"{current_dir}/Data/Voice.html"

# chrome_options = Options()
# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
# chrome_options.add_argument(f'user-agent={user_agent}')
# chrome_options.add_argument("--use-fake-ui-for-media-stream")
# chrome_options.add_argument("--use-fake-device-for-media-stream")
# chrome_options.add_argument("--headless=new")

# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=chrome_options)

# def QueryModifier(Query):
#     new_query = Query.lower().strip()
#     question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

#     if any(word + " " in new_query for word in question_words):
#         new_query += "?" if not new_query.endswith(("?", ".", "!")) else ""
#     else:
#         new_query += "." if not new_query.endswith(("?", ".", "!")) else ""

#     return new_query.capitalize()

# # Named Entity Recognition (NER)
# def extract_entities(text):
#     doc = nlp(text)
#     entities = [ent.text for ent in doc.ents]
#     return f"Recognized entities: {', '.join(entities)}" if entities else ""

# # Function to recognize and process speech
# def SpeechRecognition():
#     driver.get("file:///" + Link)
#     driver.find_element(by=By.ID, value="start").click()

#     while True:
#         try:
#             Text = driver.find_element(by=By.ID, value="output").text

#             if Text:
#                 driver.find_element(by=By.ID, value="end").click()

#                 if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
#                     processed_text = QueryModifier(Text) + " " + extract_entities(Text)
#                     return processed_text
#                 else:
#                     translated_text = mt.translate(Text, "en")
#                     return QueryModifier(translated_text) + " " + extract_entities(translated_text)

#         except Exception as e:
#             pass

# if __name__ == "__main__":
#     while True:
#         recognized_text = SpeechRecognition()
#         print(recognized_text)
