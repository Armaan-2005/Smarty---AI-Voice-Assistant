import time
import webbrowser
import threading
import speech_recognition as sr
import pyttsx3
import pyautogui
import psutil
import requests
from datetime import datetime
import pywhatkit

#Local Model

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"


#Speak Method

def speak(text):
    print("Smarty:", text)
    t = threading.Thread(target=_speak_thread, args=(text,))
    t.daemon = True
    t.start()


def _speak_thread(text):
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)
    engine.setProperty("rate", 170)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


#Listening Method

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except:
        return ""


#Thinking Method

def think(prompt):
    try:
        full_prompt = f"""You are Smarty, a witty and helpful voice assistant. Keep responses brief and conversational , do not include emoji (1-2 sentences max).

User: {prompt}
Smarty:"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=25
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "I'm thinking...").strip()
        else:
            return "I'm having trouble processing that request."

    except requests.exceptions.ConnectionError:
        return "I can't connect to my AI brain. Is Ollama running?"
    except Exception as e:
        print(f"Error in think(): {e}")
        return "Something went wrong with my thinking process."

#Apps Management

def close_app(app_name):
    for proc in psutil.process_iter(['name']):
        try:
            if app_name.lower() in proc.info['name'].lower():
                proc.kill()
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def play_on_spotify(query):
    speak(f"Playing {query} on Spotify.")
    search_url = f"https://open.spotify.com/search/{query}"
    webbrowser.open(search_url)

#START

time.sleep(1)
speak("Smarty AI system online, Hello Sir!.")

#MAIN LOOP

while True:
    command = listen()
    if not command:
        continue

    # BASIC TALKBACK & GREETINGS

    if command in ["hi", "hello", "hey smarty","smarty"]:
        speak("Hello Sir! How can I make your day easier?")
        continue

    # EXIT / STOP

    if any(word in command for word in ["exit", "stop", "shutdown", "bye"]):
        speak("Goodbye Sir. Smarty shutting down.")
        time.sleep(6)
        break

    # DATE & TIME

    elif "time" in command:
        speak(datetime.now().strftime("The time is %I:%M %p"))
        continue

    elif "date" in command:
        speak(datetime.now().strftime("Today is %d %B %Y"))
        continue

    elif "hear" in command:
        speak("Yes Sir , Loud and Clear!")
        continue

    # OPENING APPS / WEB

    elif "open" in command:
        if "youtube" in command:
            speak("Opening YouTube")
            webbrowser.open("https://youtube.com")
        elif "google" in command:
            speak("Opening Google")
            webbrowser.open("https://google.com")
        elif "instagram" in command:
            speak("Opening Instagram")
            webbrowser.open("https://instagram.com")
        elif "whatsapp" in command:
            speak("Opening WhatsApp")
            webbrowser.open("https://web.whatsapp.com/")
        else:
            app = command.replace("open ", "")
            speak(f"Searching for {app}")
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write(app)
            pyautogui.press('enter')
        continue

    # MINIMIZING & CLOSING

    elif "minimize" in command or "hide" in command:
        speak("Minimizing applications.")
        pyautogui.hotkey('win', 'd')
        continue

    elif "close" in command:
        if "window" in command or "browser" in command:
            speak("Closing current window.")
            pyautogui.hotkey('alt', 'f4')
        else:
            app_to_close = command.replace("close ", "").strip()
            if close_app(app_to_close):
                speak(f"Closed {app_to_close}")
            else:
                speak(f"I couldn't find {app_to_close} running.")
        continue

    # TYPING FUNCTIONS

    elif "type" in command or "write" in command:
        text_to_type = command.replace("type ", "").replace("write ", "")
        speak(f"Typing now.")
        time.sleep(1)  # Time to switch to target window
        pyautogui.write(text_to_type, interval=0.1)
        continue

    # NEWS
    elif "news"in command or "today" in command:
        speak("Fetching today's headlines from Google News.")
        webbrowser.open("https://news.google.com")
        continue

    # CALLING (WHATSAPP)
    elif "call" in command:
        person = command.replace("call ", "").replace("on whatsapp", "").strip()
        speak(f"Initiating contact with {person} on WhatsApp.")
        webbrowser.open(f"https://web.whatsapp.com/send?phone=&text=Hello_{person}")

    # PLAYING YOUTUBE VIDEOS

    elif "play video" in command or "youtube" in command or "video" in command:
        query = command.replace("play ", "")
        speak(f"Playing {query} on YouTube.")
        pywhatkit.playonyt(query)
        continue
    
    # PLAYING SONGS (SPOTIFY)

    elif "play song" in command or "play music" in command or "spotify"in command:
        song = command.replace("play song", "").replace("play music", "").replace("play", "").strip()
        if song:
            play_on_spotify(song)
        else:
            webbrowser.open("https://open.spotify.com/")
        continue

    # AI THINKING / GENERAL CHAT
    else:
        answer = think(command)
        speak(answer)

    time.sleep(1)