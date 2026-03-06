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
conversation_history = []
is_speaking = False
pause_requested = False

#Speak Method

def speak(text):
    global is_speaking, pause_requested
    if pause_requested:
        return
    print("Smarty:", text)
    is_speaking = True
    t = threading.Thread(target=_speak_thread, args=(text,))
    t.daemon = True
    t.start()
    t.join()  # Wait for speech to finish before continuing
    is_speaking = False


def _speak_thread(text):
    global pause_requested
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)
    engine.setProperty("rate", 170)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


#Listening Method

def listen():
    global pause_requested, is_speaking
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""
        
    try:
        command = r.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except:
        return ""


#Thinking Method

def think(prompt):
    try:
        full_prompt = f"""You are Smarty, a smart and informative voice assistant. Keep responses brief and conversational , do not include emojis (3-5 sentences max).

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

    if any(word in command for word in ["exit", "stop", "shutdown", "shut down","off", "bye"]):
        speak("Goodbye Sir. Smarty shutting down.")
        time.sleep(3)
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

    elif "minimize" in command or "hide" in command or "minimise" in command:
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

    elif "type" in command or "write" in command or "print" in command:
        text_to_type = command.replace("type ", "").replace("write ", "").replace("print","")
        speak(f"Typing now.")
        time.sleep(1)  # Time to switch to target window
        pyautogui.write(text_to_type, interval=0.1)
        continue

    # NEWS
    elif "news" in command:
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
        speak(f"Playing {query} on YouTube Browser.")
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
    
    # SYSTEM STATUS

    elif "system status" in command or "performance" in command:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        speak(f"CPU is at {cpu} percent. RAM usage is {ram} percent.")
        continue
    
    # SYSTEM VOLUME
 
    elif "volume up" in command:
        for _ in range(5): pyautogui.press("volumeup")
        speak("Volume increased.")
        continue

    elif "volume down" in command:
        for _ in range(5): pyautogui.press("volumedown")
        speak("Volume decreased.")
        continue

    elif "mute" in command:
        pyautogui.press("volumemute")
        speak("Muted.")
        continue

    # AI THINKING / GENERAL CHAT
    else:
        conversation_history.append(f"User: {command}")
        
        # Build context from history
        context = "\n".join(conversation_history[-6:])  # Last 6 exchanges
        response = think(context)
        
        conversation_history.append(f"Smarty: {response}")
        speak(response)
        time.sleep(1)