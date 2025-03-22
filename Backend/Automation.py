from AppOpener import close, open as appopen, give_appnames
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

# User-Agent for making web requests
useragent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
             '(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36')

def GoogleSearch(topic):
    """Perform a Google search."""
    search(topic)
    return True

def YouTubeSearch(topic):
    """Search for a topic on YouTube."""
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)
    return True

def PlayYoutube(query):
    """Play a YouTube video."""
    playonyt(query)
    return True

def extract_links(html):
    """Extracts links from Google search results."""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', {'jsname': 'UWckNb'})
    return [link.get('href') for link in links]

def search_google(query, session):
    """Perform a Google search and return HTML content."""
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": useragent}
    
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print("❌ Failed to retrieve search results.")
        return None

def OpenApp(app, sess=requests.session()):
    """Opens an application or a website if the app is not found."""
    app = app.lower().strip()

    try:
        available_apps = give_appnames()  # Get installed apps
        if app in available_apps:
            print(f"🟢 Opening {app}...")
            appopen(app, match_closest=True, output=True, throw_error=True)
            return True
        else:
            print(f"⚠️ App '{app}' not found. Searching online instead...")
    except Exception as e:
        print(f"❌ Error opening '{app}': {e}")

    # If app not found, try searching online
    html = search_google(app, sess)
    links = extract_links(html)

    if links:
        print("🔵 Opening first search result...")
        webopen(links[0])
    else:
        print("⚠️ No search results found.")

    return True

def CloseApp(app):
    """Closes an application."""
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        print(f"⚠️ Could not close {app}.")
        return False

def System(command):
    """Executes system commands like volume control."""
    if command == "mute":
        keyboard.press_and_release("volume mute")
    elif command == "unmute":
        keyboard.press_and_release("volume mute")
    elif command == "volume up":
        keyboard.press_and_release("volume up")
    elif command == "volume down":
        keyboard.press_and_release("volume down")

    return True

async def TranslateAndExecute(commands):
    """Translates user commands and executes them asynchronously."""
    funcs = []

    for command in commands:
        if command.startswith("open "):
            app_name = command.removeprefix("open ")
            fun = asyncio.to_thread(OpenApp, app_name)
            funcs.append(fun)
        
        elif command.startswith("close "):
            app_name = command.removeprefix("close ")
            fun = asyncio.to_thread(CloseApp, app_name)
            funcs.append(fun)

        elif command.startswith("play "):
            query = command.removeprefix("play ")
            fun = asyncio.to_thread(PlayYoutube, query)
            funcs.append(fun)

        elif command.startswith("google search "):
            query = command.removeprefix("google search ")
            fun = asyncio.to_thread(GoogleSearch, query)
            funcs.append(fun)

        elif command.startswith("youtube search "):
            query = command.removeprefix("youtube search ")
            fun = asyncio.to_thread(YouTubeSearch, query)
            funcs.append(fun)

        elif command.startswith("system "):
            sys_command = command.removeprefix("system ")
            fun = asyncio.to_thread(System, sys_command)
            funcs.append(fun)

        else:
            print(f"⚠️ No function found for: {command}")

    results = await asyncio.gather(*funcs)
    
    for result in results:
        yield result

async def Automation(commands):
    """Automates the execution of a list of commands."""
    async for result in TranslateAndExecute(commands):
        pass
    return True
