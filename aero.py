import pyttsx3
import wikipedia
import speech_recognition as sr
import webbrowser
import datetime
import os
import sys
import smtplib
import shutil
from news import speak_news, getNewsUrl
from OCR import OCR
from diction import translate
from helpers import *
from youtube import youtube
from sys import platform
import getpass
from face_recognition_tools import FaceRecognitionError, recognize_once

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)
except Exception:
    engine = None
    voices = []

# print(voices[0].id)

class AeroAI:
    def __init__(self) -> None:
        self.browser_name = None
        chrome_path = self._find_chrome()
        if chrome_path:
            webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
            self.browser_name = 'chrome'

    def _find_chrome(self):
        if platform in ("linux", "linux2"):
            candidates = [shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser')]
        elif platform == "darwin":
            candidates = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
        elif platform == "win32":
            candidates = [
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
            ]
        else:
            candidates = []
        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    def open_url(self, url):
        if self.browser_name:
            webbrowser.get(self.browser_name).open_new_tab(url)
        else:
            webbrowser.open_new_tab(url)

    def wishMe(self) -> None:
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            speak("Good Morning SIR")
        elif hour >= 12 and hour < 18:
            speak("Good Afternoon SIR")

        else:
            speak('Good Evening SIR')

        weather()
        speak('I am AeroA.I. Please tell me how can I help you SIR?')

    def sendEmail(self, to, content) -> None:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('email', 'password')
        server.sendmail('email', to, content)
        server.close()

    def execute_query(self, query):
        # TODO: make this more concise
        if 'wikipedia' in query:
            speak('Searching Wikipedia....')
            query = query.replace('wikipedia', '')
            results = wikipedia.summary(query, sentences=2)
            speak('According to Wikipedia')
            print(results)
            speak(results)
        elif 'youtube downloader' in query:
            exec(open('youtube_downloader.py').read())
            
        
            
        elif 'voice' in query:
            if 'female' in query:
                if len(voices) > 1 and engine:
                    engine.setProperty('voice', voices[1].id)
            elif voices and engine:
                engine.setProperty('voice', voices[0].id)
            speak("Hello Sir, I have switched my voice. How is it?")

        if 'aero are you there' in query:
            speak("Yes Sir, at your service")
        if 'aero who made you' in query:
            speak("Yes Sir, my master build me in AI")
            
         

        elif 'open youtube' in query:

            self.open_url('https://youtube.com')
            
        elif 'open amazon' in query:
            self.open_url('https://amazon.com')

        elif 'cpu' in query:
            cpu()

        elif 'joke' in query:
            joke()

        elif 'screenshot' in query:
            speak("taking screenshot")
            screenshot()

        elif 'open google' in query:
            self.open_url('https://google.com')

        elif 'open stackoverflow' in query:
            self.open_url('https://stackoverflow.com')

        elif 'play music' in query:
            music_path = os.getenv('AERO_MUSIC_PATH')
            if music_path and os.path.exists(music_path):
                os.startfile(music_path)
            else:
                speak('Set AERO_MUSIC_PATH to a music file first.')

        elif 'search youtube' in query:
            speak('What you want to search on Youtube?')
            youtube(takeCommand())
        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f'Sir, the time is {strTime}')

        elif 'search' in query:
            speak('What do you want to search for?')
            search = takeCommand()
            url = 'https://google.com/search?q=' + search
            self.open_url(url)
            speak('Here is What I found for' + search)

        elif 'location' in query:
            speak('What is the location?')
            location = takeCommand()
            url = 'https://google.nl/maps/place/' + location + '/&amp;'
            self.open_url(url)
            speak('Here is the location ' + location)

        elif 'your master' in query:
            if platform == "win32" or "darwin":
                speak('Aayan is my master. He created me couple of days ago')
            elif platform == "linux" or platform == "linux2":
                name = getpass.getuser()
                speak(name, 'is my master. He is running me right now')

        elif 'your name' in query:
            speak('My name is AeroA.I')
        elif 'who made you' in query:
            speak('I was created by my AI master in 2021')
            
        elif 'stands for' in query:
            speak('AeroA.I stands for AERO ARTIFICIAL INTELLIGENCE')
        elif 'open code' in query:
            if platform == "win32":
                os.startfile(
                    "C:\\Users\\gs935\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
            elif platform == "linux" or platform == "linux2" or "darwin":
                os.system('code .')

        elif 'shutdown' in query:
            if platform == "win32":
                os.system('shutdown /p /f')
            elif platform == "linux" or platform == "linux2" or "darwin":
                os.system('poweroff')

        elif 'cpu' in query:
            cpu()
        elif 'your friend' in query:
            speak('My friends are Google assisstant alexa and siri')

        elif 'joke' in query:
            joke()

        elif 'screenshot' in query:
            speak("taking screenshot")
            screenshot()

        elif 'github' in query:
            self.open_url('https://github.com')

        elif 'remember that' in query:
            speak("what should i remember sir")
            rememberMessage = takeCommand()
            speak("you said me to remember"+rememberMessage)
            remember = open('data.txt', 'w')
            remember.write(rememberMessage)
            remember.close()

        elif 'do you remember anything' in query:
            remember = open('data.txt', 'r')
            speak("you said me to remember that" + remember.read())

        elif 'sleep' in query:
            sys.exit()

        elif 'dictionary' in query:
            speak('What you want to search in your intelligent dictionary?')
            translate(takeCommand())

        elif 'news' in query:
            speak('Ofcourse sir..')
            speak_news()
            speak('Do you want to read the full news...')
            test = takeCommand()
            if 'yes' in test:
                speak('Ok Sir, Opening browser...')
                webbrowser.open(getNewsUrl())
                speak('You can now read the full news from this website.')
            else:
                speak('No Problem Sir')

        elif 'voice' in query:
            if 'female' in query:
                if voices and engine:
                    engine.setProperty('voice', voices[0].id)
            elif len(voices) > 1 and engine:
                engine.setProperty('voice', voices[1].id)
            speak("Hello Sir, I have switched my voice. How is it?")

        elif 'email to aayan' in query:
            try:
                speak('What should I say?')
                content = takeCommand()
                to = 'email'
                self.sendEmail(to, content)
                speak('Email has been sent!')

            except Exception as e:
                speak('Sorry sir, Not able to send email at the moment')


def wakeUpAeroAI():
    bot_ = AeroAI()
    bot_.wishMe()
    while True:
        query = takeCommand().lower()
        bot_.execute_query(query)


def authenticate_with_face():
    try:
        result = recognize_once(timeout_seconds=15, confidence_threshold=65, show_window=True)
    except FaceRecognitionError as exc:
        speak(str(exc) + ' Starting without face authentication.')
        return True
    except Exception as exc:
        speak('Face authentication failed: ' + str(exc) + '. Starting without face authentication.')
        return True

    if result['recognized']:
        speak('Optical Face Recognition Done. Welcome ' + result['name'])
        return True

    speak('Optical Face Recognition Failed')
    return False

if __name__ == '__main__':
    if '--no-auth' in sys.argv or authenticate_with_face():
        wakeUpAeroAI()
