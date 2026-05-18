#!/usr/bin/env python3
"""
AeroA.I Lite - minimal assistant that runs without heavy dependencies.
Commands:
 - help: show commands
 - time: show current time
 - open youtube/google: open sites
 - search <query>: web search
 - wikipedia <topic>: try to use wikipedia package or fallback to web search
 - name / who are you: assistant name
 - who made you: author
 - start full: attempt to start full aero.py (in background)
 - say <text>: print/speak text
 - exit/quit/sleep: exit
"""

import sys
import webbrowser
import datetime
import shlex
import subprocess
import os

# optional voice
try:
    import pyttsx3
    _engine = pyttsx3.init()
    def speak(t):
        print(t)
        try:
            _engine.say(t)
            _engine.runAndWait()
        except Exception:
            pass
except Exception:
    _engine = None
    def speak(t):
        print(t)


def wish():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak('Good morning, Sir')
    elif hour < 18:
        speak('Good afternoon, Sir')
    else:
        speak('Good evening, Sir')
    speak('AeroA.I Lite ready. Type "help" for commands.')


def try_wikipedia(query):
    try:
        import wikipedia
        res = wikipedia.summary(query, sentences=2)
        speak(res)
    except Exception:
        speak('Could not fetch Wikipedia summary; opening web search instead.')
        webbrowser.open('https://google.com/search?q=' + webbrowser.quote(query))


def start_full():
    # Try to start full aero.py using the venv if available, else py -3, else python
    cwd = os.getcwd()
    venv_py = os.path.join(cwd, '.venv', 'Scripts', 'python.exe')
    cmd = None
    if os.path.exists(venv_py):
        cmd = [venv_py, 'aero.py']
    else:
        # try py -3 then python
        cmd = ['py', '-3', 'aero.py']
    try:
        # start detached
        subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        speak('Attempted to start full AeroA.I in background.')
    except Exception as e:
        speak('Failed to start full AeroA.I: ' + str(e))


def repl():
    while True:
        try:
            text = input('AeroLite> ').strip()
        except (EOFError, KeyboardInterrupt):
            speak('\nExiting AeroA.I Lite. Goodbye.')
            break
        if not text:
            continue
        parts = shlex.split(text)
        cmd = parts[0].lower()
        args = parts[1:]
        if cmd in ('help', '?'):
            print('Commands: help, time, open youtube, open google, search <q>, wikipedia <topic>, name, who made you, start full, say <text>, exit')
        elif cmd == 'time':
            speak('Current time is ' + datetime.datetime.now().strftime('%H:%M:%S'))
        elif text.lower() in ('open youtube', 'open youtube()') or (cmd=='open' and args and args[0].lower()=='youtube'):
            webbrowser.open('https://youtube.com')
        elif text.lower() in ('open google',) or (cmd=='open' and args and args[0].lower()=='google'):
            webbrowser.open('https://google.com')
        elif cmd == 'search' and args:
            q = ' '.join(args)
            webbrowser.open('https://google.com/search?q=' + webbrowser.quote(q))
        elif cmd == 'wikipedia' and args:
            q = ' '.join(args)
            try:
                import wikipedia
                speak('Searching Wikipedia for ' + q)
                res = wikipedia.summary(q, sentences=2)
                speak(res)
            except Exception:
                speak('Wikipedia not available; opening web search')
                webbrowser.open('https://google.com/search?q=' + webbrowser.quote(q))
        elif cmd in ('name', 'yourname', 'who') and 'name' in text.lower():
            speak('My name is AeroA.I')
        elif text.lower() in ('who made you', 'who made you?'):
            speak('I was created by Aayan')
        elif cmd == 'start' and args and args[0].lower()=='full':
            start_full()
        elif cmd == 'say' and args:
            speak(' '.join(args))
        elif cmd in ('exit', 'quit', 'sleep'):
            speak('Shutting down AeroA.I Lite. Goodbye.')
            break
        else:
            speak('Unknown command. Type help for commands.')


if __name__ == '__main__':
    wish()
    repl()
