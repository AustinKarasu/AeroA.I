import json
from pathlib import Path

import geocoder
import psutil
import pyautogui
import pyjokes
import pyttsx3
import requests
import speech_recognition as sr
from difflib import get_close_matches


BASE_DIR = Path(__file__).resolve().parent
SCREENSHOT_DIR = BASE_DIR / 'screenshots'

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)
except Exception:
    engine = None

with open(BASE_DIR / 'data.json', encoding='utf-8') as data_file:
    data = json.load(data_file)

def speak(audio) -> None:
    print(audio)
    if engine is None:
        return
    try:
        engine.say(audio)
        engine.runAndWait()
    except Exception:
        pass

def screenshot() -> None:
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    img = pyautogui.screenshot()
    path = SCREENSHOT_DIR / 'screenshot.png'
    img.save(path)
    speak(f'Screenshot saved to {path}')

def cpu() -> None:
    usage = str(psutil.cpu_percent())
    speak("CPU is at"+usage)

    battery = psutil.sensors_battery()
    if battery is None:
        speak("Battery information is not available on this device")
    else:
        speak("battery is at")
        speak(str(battery.percent))

def joke() -> None:
    for i in range(5):
        speak(pyjokes.get_jokes()[i])

def takeCommand() -> str:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        r.pause_threshold = 1
        r.energy_threshold = 494
        r.adjust_for_ambient_noise(source, duration=1.5)
        audio = r.listen(source)

    try:
        print('Recognizing..')
        query = r.recognize_google(audio, language='en-in')
        print(f'User said: {query}\n')

    except Exception as e:
        # print(e)

        print('Say that again please...')
        return 'None'
    return query

def weather():
    try:
        g = geocoder.ip('me')
        if not g.latlng:
            speak('Weather location is not available')
            return
        api_url = (
            "https://fcc-weather-api.glitch.me/api/current?lat="
            + str(g.latlng[0])
            + "&lon="
            + str(g.latlng[1])
        )
        response = requests.get(api_url, timeout=10)
        data_json = response.json()
        if data_json.get('cod') == 200:
            main = data_json['main']
            wind = data_json['wind']
            weather_desc = data_json['weather'][0]
            speak(str(data_json['coord']['lat']) + 'latitude' + str(data_json['coord']['lon']) + 'longitude')
            speak('Current location is ' + data_json['name'] + data_json['sys']['country'])
            speak('weather type ' + weather_desc['main'])
            speak('Wind speed is ' + str(wind['speed']) + ' metre per second')
            speak('Temperature: ' + str(main['temp']) + 'degree celcius')
            speak('Humidity is ' + str(main['humidity']))
        else:
            speak('Weather is not available right now')
    except Exception:
        speak('Weather is not available right now')


def translate(word):
    word = word.lower()
    if word in data:
        speak(data[word])
    elif len(get_close_matches(word, data.keys())) > 0:
        x = get_close_matches(word, data.keys())[0]
        speak('Did you mean ' + x +
              ' instead,  respond with Yes or No.')
        ans = takeCommand().lower()
        if 'yes' in ans:
            speak(data[x])
        elif 'no' in ans:
            speak("Word doesn't exist. Please make sure you spelled it correctly.")
        else:
            speak("We didn't understand your entry.")

    else:
        speak("Word doesn't exist. Please double check it.")
