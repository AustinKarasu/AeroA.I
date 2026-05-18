import requests
import json
import os
import pyttsx3

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)
except Exception:
    engine = None


def speak(audio):
    print(audio)
    if engine is None:
        return
    try:
        engine.say(audio)
        engine.runAndWait()
    except Exception:
        pass


def getNewsUrl():
    api_key = os.getenv('NEWS_API_KEY', '').strip()
    if not api_key:
        return 'https://news.google.com/topstories'
    return 'https://newsapi.org/v2/top-headlines?sources=the-times-of-india&apiKey=' + api_key


def speak_news():
    url = getNewsUrl()
    if 'newsapi.org' not in url:
        speak('NEWS_API_KEY is not configured. Opening Google News instead.')
        return
    news = requests.get(url, timeout=10).text
    news_dict = json.loads(news)
    arts = news_dict.get('articles', [])
    if not arts:
        speak('No news headlines are available right now.')
        return
    speak('Source: The Times Of India')
    speak("Today's Headlines are..")
    for index, articles in enumerate(arts):
        speak(articles['title'])
        if index == len(arts)-1:
            break
        speak('Moving on the next news headline..')
    speak('These were the top headlines, Have a nice day Sir!!..')

if __name__ == '__main__':
    speak_news()
