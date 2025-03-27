from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QLabel, 
                            QVBoxLayout, QWidget, QPushButton)
from PyQt5.QtGui import QMovie, QPixmap, QFont, QColor, QIcon, QPalette
from PyQt5.QtCore import Qt, QTimer, QSize
import os
import sys

# --- Utility Functions ---
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", 
                     "which", "whose", "whom", "can you", "what's", 
                     "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# --- File Operations ---
def TempDirectoryPath(Filename):
    current_dir = os.getcwd()
    return os.path.join(current_dir, "Frontend", "Files", Filename)

def ShowTextToScreen(Text):
    with open(TempDirectoryPath('Responses.data'), "w", encoding="utf-8") as file:
        file.write(Text)

def SetMicrophoneStatus(Command):
    with open(TempDirectoryPath('Mic.data'), "w", encoding="utf-8") as file:
        file.write(Command)

def GetMicrophoneStatus():
    try:
        with open(TempDirectoryPath('Mic.data'), "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "False"

def SetAssistantStatus(Status):
    with open(TempDirectoryPath('Status.data'), "w", encoding="utf-8") as file:
        file.write(Status)

def GetAssistantStatus():
    try:
        with open(TempDirectoryPath('Status.data'), "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Available..."

# --- Main Window Class ---
class VoiceAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS Voice Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Set black background
        self.setStyleSheet("background-color: black;")
        
        # Main widget and layout
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: black;")
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 18px; 
            color: white;
            margin: 10px;
        """)
        layout.addWidget(self.status_label)
        
        # GIF display
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        gif_path = os.path.join("Frontend", "Graphics", "Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(400, 225))
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setText("JARVIS GIF not found")
            self.gif_label.setStyleSheet("color: white;")
        layout.addWidget(self.gif_label)
        
        # Text display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("""
            background-color: #111;
            color: white;
            font-size: 16px;
            border: 2px solid #333;
            border-radius: 10px;
            padding: 10px;
        """)
        layout.addWidget(self.text_display, stretch=1)
        
        # Mic button (larger size)
        self.mic_button = QPushButton()
        mic_icon_path = os.path.join("Frontend", "Graphics", "Mic_on.png")
        if os.path.exists(mic_icon_path):
            self.mic_button.setIcon(QIcon(mic_icon_path))
            self.mic_button.setIconSize(QSize(80, 80))
        self.mic_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                min-width: 100px;
                min-height: 100px;
            }
            QPushButton:hover {
                background: #333;
                border-radius: 50px;
            }
        """)
        self.mic_button.clicked.connect(self.toggle_mic)
        layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        
        # Set up file monitoring
        self.setup_file_monitors()
        
        # Create required directories if they don't exist
        os.makedirs(os.path.join("Frontend", "Files"), exist_ok=True)
        
        # Initialize mic state file
        self.mic_file = TempDirectoryPath('Mic.data')
        with open(self.mic_file, "w") as f:
            f.write("True")  # Start in listening mode
    
    def setup_file_monitors(self):
        """Set up file monitoring timers"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(100)
        
        self.response_timer = QTimer()
        self.response_timer.timeout.connect(self.update_response)
        self.response_timer.start(100)
    
    def update_status(self):
        """Update status from Status.data"""
        try:
            with open(TempDirectoryPath('Status.data'), "r") as f:
                status = f.read().strip()
                if status:
                    self.status_label.setText(status)
        except FileNotFoundError:
            pass
    
    def update_response(self):
        """Update text from Responses.data"""
        try:
            with open(TempDirectoryPath('Responses.data'), "r") as f:
                response = f.read().strip()
                if response:
                    self.text_display.append(response)
                    # Clear the file after reading
                    with open(TempDirectoryPath('Responses.data'), "w") as f:
                        f.write("")
        except FileNotFoundError:
            pass
    
    def toggle_mic(self):
        """Toggle microphone state"""
        current_state = GetMicrophoneStatus() == "True"
        SetMicrophoneStatus("False" if current_state else "True")
        self.update_mic_icon(not current_state)
    
    def update_mic_icon(self, state):
        """Update microphone icon based on state"""
        icon = "Mic_on.png" if state else "Mic_off.png"
        icon_path = os.path.join("Frontend", "Graphics", icon)
        if os.path.exists(icon_path):
            self.mic_button.setIcon(QIcon(icon_path))
            self.mic_button.setIconSize(QSize(80, 80))
        self.status_label.setText("Listening..." if state else "Microphone off")

def GraphicalUserInterface():
    """Legacy function for Main.py compatibility"""
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(palette)
    
    window = VoiceAssistantGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()