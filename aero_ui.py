import datetime
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import ttk
from urllib.parse import parse_qs, quote, quote_plus, unquote, urlparse

import requests
import speech_recognition as sr
from bs4 import BeautifulSoup

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    import wikipedia
except Exception:
    wikipedia = None

from news import getNewsUrl, speak_news
from youtube import youtube
from face_recognition_tools import FaceRecognitionError, recognize_once


BASE_DIR = Path(__file__).resolve().parent
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434').rstrip('/')
OLLAMA_MODEL = os.getenv('AERO_OLLAMA_MODEL', 'llama3.2:1b')
FAST_MODEL_HINTS = ('1b', '1.5b', '2b', '3b', 'mini', 'tiny', 'phi3', 'gemma2:2b')
CURRENT_HINTS = (
    'latest',
    'current',
    'today',
    "today's",
    'now',
    'new',
    'recent',
    'breaking',
    'news',
    '2026',
    'price',
    'score',
    'weather',
    'president',
    'ceo',
    'version',
)
APP_ALIASES = {
    'chrome': ['chrome', 'google chrome'],
    'edge': ['msedge', 'microsoft edge'],
    'firefox': ['firefox'],
    'spotify': ['spotify:', 'spotify'],
    'netflix': ['netflix:', 'netflix'],
    'whatsapp': ['whatsapp:', 'whatsapp'],
    'telegram': ['tg:', 'telegram'],
    'discord': ['discord:', 'discord'],
    'notepad': ['notepad'],
    'calculator': ['calc', 'calculator'],
    'paint': ['mspaint', 'paint'],
    'word': ['winword', 'word'],
    'excel': ['excel'],
    'powerpoint': ['powerpnt', 'powerpoint'],
    'vscode': ['code', 'visual studio code'],
    'vs code': ['code', 'visual studio code'],
}


def default_ollama_model():
    configured = os.getenv('AERO_OLLAMA_MODEL', '').strip()
    if configured:
        return configured
    try:
        response = requests.get(OLLAMA_HOST + '/api/tags', timeout=2)
        response.raise_for_status()
        models = [item.get('name', '') for item in response.json().get('models', [])]
        for model in models:
            if any(hint in model.lower() for hint in FAST_MODEL_HINTS):
                return model
        if models:
            return models[0] or OLLAMA_MODEL
    except Exception:
        pass
    return OLLAMA_MODEL


class Speaker:
    def __init__(self):
        self.enabled = tk.BooleanVar(value=True)
        self._engine = None
        if pyttsx3 is not None:
            try:
                self._engine = pyttsx3.init()
            except Exception:
                self._engine = None

    def say(self, text):
        if self._engine is None:
            return
        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception:
            pass


class AeroUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('AeroA.I')
        self.geometry('980x640')
        self.minsize(860, 560)
        self.configure(bg='#0f1419')

        self.speaker = Speaker()
        self.events = queue.Queue()
        self.ollama_model_value = default_ollama_model()
        self.ollama_model = tk.StringVar(value=self.ollama_model_value)
        self.ollama_model.trace_add('write', self._sync_settings)
        self.fast_replies_value = True
        self.fast_replies = tk.BooleanVar(value=True)
        self.fast_replies.trace_add('write', self._sync_settings)
        self.live_web_value = True
        self.live_web = tk.BooleanVar(value=True)
        self.live_web.trace_add('write', self._sync_settings)
        self.status_text = tk.StringVar(value='Ready')
        self.start_apps_cache = None
        self.logo_image = None
        self._build_style()
        self._build_ui()
        self._greet()
        threading.Thread(target=self._warm_ollama, daemon=True).start()
        self.after(120, self._drain_events)

    def _sync_settings(self, *_args):
        self.ollama_model_value = self.ollama_model.get().strip() or OLLAMA_MODEL
        self.fast_replies_value = bool(self.fast_replies.get())
        self.live_web_value = bool(self.live_web.get())

    def _build_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#0f1419')
        self.style.configure('Panel.TFrame', background='#171e26', relief='flat')
        self.style.configure('Subtle.TFrame', background='#121820')
        self.style.configure('TLabel', background='#0f1419', foreground='#edf3f8')
        self.style.configure('Muted.TLabel', background='#0f1419', foreground='#92a3b3')
        self.style.configure('Panel.TLabel', background='#171e26', foreground='#edf3f8')
        self.style.configure('Small.Panel.TLabel', background='#171e26', foreground='#92a3b3', font=('Segoe UI', 9))
        self.style.configure('Status.TLabel', background='#121820', foreground='#aab8c5', font=('Segoe UI', 9))
        self.style.configure('TButton', padding=(12, 9), font=('Segoe UI', 10), background='#25313d', foreground='#edf3f8')
        self.style.map('TButton', background=[('active', '#303f4e')], foreground=[('active', '#ffffff')])
        self.style.configure('Accent.TButton', background='#2f8f83', foreground='#ffffff')
        self.style.map('Accent.TButton', background=[('active', '#35a193')], foreground=[('active', '#ffffff')])
        self.style.configure('Quiet.TButton', background='#1d2630', foreground='#d9e3ea')
        self.style.map('Quiet.TButton', background=[('active', '#273441')])
        self.style.configure('TCheckbutton', background='#0f1419', foreground='#edf3f8')
        self.style.configure('Panel.TCheckbutton', background='#171e26', foreground='#edf3f8')
        self.style.configure('TEntry', padding=(8, 7), fieldbackground='#f5f8fb', foreground='#102030')

    def _build_ui(self):
        root = ttk.Frame(self, padding=24)
        root.pack(fill='both', expand=True)
        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        header = ttk.Frame(root)
        header.grid(row=0, column=0, sticky='ew')
        header.columnconfigure(0, weight=1)

        title_box = ttk.Frame(header)
        title_box.grid(row=0, column=0, sticky='ew')
        logo_path = BASE_DIR / 'images' / 'aero.png'
        if logo_path.exists():
            try:
                self.logo_image = tk.PhotoImage(file=str(logo_path)).subsample(9, 9)
                ttk.Label(title_box, image=self.logo_image).pack(side='left', padx=(0, 16))
            except Exception:
                self.logo_image = None

        title_text = ttk.Frame(title_box)
        title_text.pack(side='left', fill='x', expand=True)
        ttk.Label(title_text, text='AeroA.I', font=('Segoe UI Semibold', 24)).pack(anchor='w')
        ttk.Label(
            title_text,
            text='Local assistant with Ollama, voice input, and face recognition.',
            style='Muted.TLabel',
            font=('Segoe UI', 10),
        ).pack(anchor='w', pady=(4, 0))

        toggles = ttk.Frame(header)
        toggles.grid(row=0, column=1, sticky='e')
        ttk.Checkbutton(toggles, text='Fast replies', variable=self.fast_replies).grid(row=0, column=0, sticky='e')
        ttk.Checkbutton(toggles, text='Live web', variable=self.live_web).grid(row=0, column=1, sticky='e', padx=(14, 0))
        ttk.Checkbutton(toggles, text='Speak replies', variable=self.speaker.enabled).grid(row=0, column=2, sticky='e', padx=(14, 0))

        body = ttk.Frame(root)
        body.grid(row=1, column=0, sticky='nsew', pady=(22, 14))
        body.columnconfigure(0, weight=5)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        console_panel = ttk.Frame(body, style='Panel.TFrame', padding=14)
        console_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 16))
        console_panel.rowconfigure(1, weight=1)
        console_panel.columnconfigure(0, weight=1)

        ttk.Label(console_panel, text='Conversation', style='Panel.TLabel', font=('Segoe UI Semibold', 13)).grid(
            row=0, column=0, sticky='w'
        )

        self.log = tk.Text(
            console_panel,
            wrap='word',
            height=12,
            borderwidth=0,
            padx=12,
            pady=12,
            bg='#0b1015',
            fg='#eef4f8',
            insertbackground='#eef4f8',
            font=('Consolas', 10),
            selectbackground='#2f8f83',
            selectforeground='#ffffff',
        )
        self.log.grid(row=1, column=0, sticky='nsew', pady=(10, 12))
        self.log.configure(state='disabled')

        command_row = ttk.Frame(console_panel, style='Panel.TFrame')
        command_row.grid(row=2, column=0, sticky='ew')
        command_row.columnconfigure(0, weight=1)

        self.command = ttk.Entry(command_row, font=('Segoe UI', 11))
        self.command.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        self.command.bind('<Return>', lambda _event: self.run_command())
        self.command.focus_set()

        ttk.Button(command_row, text='Listen', style='Quiet.TButton', command=self.listen_for_voice).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(command_row, text='Run', style='Accent.TButton', command=self.run_command).grid(row=0, column=2)

        model_row = ttk.Frame(console_panel, style='Panel.TFrame')
        model_row.grid(row=3, column=0, sticky='ew', pady=(12, 0))
        model_row.columnconfigure(1, weight=1)
        ttk.Label(model_row, text='Model', style='Small.Panel.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Entry(model_row, textvariable=self.ollama_model).grid(row=0, column=1, sticky='ew')

        actions_panel = ttk.Frame(body, style='Panel.TFrame', padding=14)
        actions_panel.grid(row=0, column=1, sticky='nsew')
        actions_panel.columnconfigure(0, weight=1)

        ttk.Label(actions_panel, text='Actions', style='Panel.TLabel', font=('Segoe UI Semibold', 13)).grid(
            row=0, column=0, sticky='w'
        )

        actions = [
            ('Voice Input', self.listen_for_voice),
            ('Face Recognition', self.run_face_recognition),
            ('Time', lambda: self.handle_command('time')),
            ('Open Google', lambda: self.handle_command('open google')),
            ('Open YouTube', lambda: self.handle_command('open youtube')),
            ('Open Spotify', lambda: self.handle_command('open app spotify')),
            ('Open WhatsApp', lambda: self.handle_command('open app whatsapp')),
            ('News', lambda: self.handle_command('news')),
            ('Web Search', lambda: self.handle_command('web latest technology news')),
            ('Check Ollama', lambda: self.handle_command('ollama status')),
            ('Start Voice Assistant', self.start_voice_assistant),
        ]

        for index, (label, command) in enumerate(actions, start=1):
            style = 'Accent.TButton' if index <= 2 else 'TButton'
            ttk.Button(actions_panel, text=label, style=style, command=command).grid(
                row=index, column=0, sticky='ew', pady=(10 if index == 1 else 8, 0)
            )

        hint = (
            'Try: "open app spotify", "whatsapp 919876543210: hello", '
            '"web latest AI news", or ask a normal question.'
        )
        ttk.Label(
            actions_panel,
            text=hint,
            style='Panel.TLabel',
            wraplength=270,
            justify='left',
        ).grid(row=len(actions) + 1, column=0, sticky='sw', pady=(24, 0))

        status = ttk.Frame(root, style='Subtle.TFrame', padding=(12, 8))
        status.grid(row=2, column=0, sticky='ew')
        status.columnconfigure(0, weight=1)
        ttk.Label(status, textvariable=self.status_text, style='Status.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(status, text='Enter = run command', style='Status.TLabel').grid(row=0, column=1, sticky='e')

    def _greet(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = 'Good morning. AeroA.I UI is ready.'
        elif hour < 18:
            greeting = 'Good afternoon. AeroA.I UI is ready.'
        else:
            greeting = 'Good evening. AeroA.I UI is ready.'
        self.reply(greeting)

    def _write(self, text):
        self.log.configure(state='normal')
        self.log.insert('end', text + '\n')
        self.log.see('end')
        self.log.configure(state='disabled')

    def reply(self, text):
        self._write('Aero: ' + text)
        self.status_text.set('Ready')
        if self.speaker.enabled.get():
            threading.Thread(target=self.speaker.say, args=(text,), daemon=True).start()

    def note(self, text):
        self._write('Aero: ' + text)
        self.status_text.set(text)

    def listen_for_voice(self):
        self.note('Listening...')
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.7)
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language='en-in')
        except sr.WaitTimeoutError:
            self.events.put(('reply', 'I did not hear anything.'))
            return
        except sr.UnknownValueError:
            self.events.put(('reply', 'I could not understand that. Please try again.'))
            return
        except Exception as exc:
            self.events.put(('reply', 'Voice input failed: ' + str(exc)))
            return

        self.events.put(('heard', text))

    def run_face_recognition(self):
        self.note('Starting face recognition...')
        threading.Thread(target=self._face_worker, daemon=True).start()

    def _face_worker(self):
        try:
            result = recognize_once(timeout_seconds=15, confidence_threshold=65, show_window=True)
            if result['recognized']:
                self.events.put(('reply', 'Face recognized. Welcome ' + result['name'] + '.'))
            else:
                self.events.put(('reply', 'No recognized face found. Capture samples and train the model if this is a new user.'))
        except FaceRecognitionError as exc:
            self.events.put(('reply', str(exc)))
        except Exception as exc:
            self.events.put(('reply', 'Face recognition failed: ' + str(exc)))

    def run_command(self):
        text = self.command.get().strip()
        if not text:
            return
        self.command.delete(0, 'end')
        self.handle_command(text)

    def handle_command(self, text):
        self._write('You: ' + text)
        self.status_text.set('Working...')
        threading.Thread(target=self._run_command_worker, args=(text,), daemon=True).start()

    def _run_command_worker(self, text):
        query = text.strip()
        lower = query.lower()
        try:
            if lower in ('hi', 'hello', 'hey', 'hii', 'hola'):
                self.events.put(('reply', 'Hello. I am here. What would you like me to do?'))
            elif lower in ('how are you', 'how are you?', 'how are you doing'):
                self.events.put(('reply', 'I am running smoothly. Ready when you are.'))
            elif lower in ('thanks', 'thank you', 'thank you aero'):
                self.events.put(('reply', 'You are welcome.'))
            elif lower in ('bye', 'goodbye', 'exit', 'quit'):
                self.events.put(('reply', 'Goodbye. Closing the UI.'))
                self.events.put(('close', None))
            elif lower in ('help', '?'):
                self.events.put(('reply', 'Commands: time, open google, open youtube, search, web, youtube, wikipedia, news, say, ollama status, start voice. Current questions use live web when enabled.'))
            elif lower in ('ollama status', 'check ollama'):
                self._ollama_status()
            elif lower in ('time', 'the time'):
                self.events.put(('reply', 'Current time is ' + datetime.datetime.now().strftime('%H:%M:%S')))
            elif lower in ('open google', 'google'):
                webbrowser.open_new_tab('https://google.com')
                self.events.put(('reply', 'Opened Google.'))
            elif lower in ('open youtube', 'youtube'):
                webbrowser.open_new_tab('https://youtube.com')
                self.events.put(('reply', 'Opened YouTube.'))
            elif lower.startswith('open app '):
                self._open_application(query[9:].strip())
            elif lower.startswith('open '):
                target = query[5:].strip()
                if target and target not in ('google', 'youtube'):
                    self._open_application(target)
                else:
                    self.events.put(('reply', 'Tell me which app to open.'))
            elif lower.startswith('search '):
                search = query[7:].strip()
                webbrowser.open_new_tab('https://google.com/search?q=' + quote_plus(search))
                self.events.put(('reply', 'Searching Google for ' + search))
            elif lower.startswith('whatsapp ') or lower.startswith('send whatsapp '):
                self._send_whatsapp(query)
            elif lower.startswith('web '):
                self._answer_with_web(query[4:].strip())
            elif lower.startswith('youtube '):
                search = query[8:].strip()
                youtube(search)
                self.events.put(('reply', 'Searching YouTube for ' + search))
            elif lower.startswith('wikipedia '):
                topic = query[10:].strip()
                self._wikipedia(topic)
            elif lower == 'news':
                self._news()
            elif lower.startswith('say '):
                self.events.put(('reply', query[4:].strip()))
            elif lower in ('name', 'your name', 'who are you'):
                self.events.put(('reply', 'My name is AeroA.I.'))
            elif lower in ('start voice', 'start full', 'voice assistant'):
                self.events.put(('start_voice', None))
            elif self.live_web_value and self._needs_live_web(lower):
                self._answer_with_web(query)
            else:
                self._ask_ollama(query)
        except Exception as exc:
            self.events.put(('reply', 'Command failed: ' + str(exc)))

    def _needs_live_web(self, lower):
        return any(hint in lower for hint in CURRENT_HINTS)

    def _open_application(self, app_name):
        app_name = app_name.strip()
        if not app_name:
            self.events.put(('reply', 'Tell me which app to open.'))
            return

        candidates = APP_ALIASES.get(app_name.lower(), [app_name])
        for candidate in candidates:
            if self._try_open_app_candidate(candidate, app_name):
                return

        shortcut = self._find_start_menu_shortcut(app_name)
        if shortcut:
            try:
                os.startfile(shortcut)
                self.events.put(('reply', 'Opened ' + app_name + '.'))
                return
            except Exception:
                pass

        app_id = self._find_windows_store_app_id(app_name)
        if app_id:
            try:
                subprocess.Popen(['explorer.exe', 'shell:AppsFolder\\' + app_id])
                self.events.put(('reply', 'Opened ' + app_name + '.'))
                return
            except Exception:
                pass

        web_fallbacks = {
            'netflix': 'https://www.netflix.com',
            'spotify': 'https://open.spotify.com',
            'whatsapp': 'https://web.whatsapp.com',
            'telegram': 'https://web.telegram.org',
            'discord': 'https://discord.com/app',
        }
        fallback = web_fallbacks.get(app_name.lower())
        if fallback:
            webbrowser.open_new_tab(fallback)
            self.events.put(('reply', 'I could not find the app, so I opened ' + app_name + ' on the web.'))
            return

        self.events.put(('reply', 'I could not find an installed app named ' + app_name + '.'))

    def _try_open_app_candidate(self, candidate, display_name):
        try:
            if candidate.endswith(':'):
                os.startfile(candidate)
                self.events.put(('reply', 'Opened ' + display_name + '.'))
                return True

            executable = shutil.which(candidate)
            if executable:
                subprocess.Popen([executable])
                self.events.put(('reply', 'Opened ' + display_name + '.'))
                return True

            if os.name == 'nt':
                completed = subprocess.run(
                    ['powershell.exe', '-NoProfile', '-Command', 'Start-Process -FilePath $args[0]', candidate],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=4,
                )
                if completed.returncode == 0:
                    self.events.put(('reply', 'Opened ' + display_name + '.'))
                    return True
        except Exception:
            return False
        return False

    def _find_start_menu_shortcut(self, app_name):
        if os.name != 'nt':
            return None
        roots = [
            Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs',
            Path(os.environ.get('PROGRAMDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs',
        ]
        needle = app_name.lower()
        best = None
        for root in roots:
            if not root.exists():
                continue
            for shortcut in root.rglob('*.lnk'):
                name = shortcut.stem.lower()
                if needle == name:
                    return str(shortcut)
                if needle in name and best is None:
                    best = str(shortcut)
        return best

    def _find_windows_store_app_id(self, app_name):
        if os.name != 'nt':
            return None
        try:
            needle = app_name.lower()
            exact = None
            partial = None
            for item in self._get_start_apps():
                name = str(item.get('Name', '')).lower()
                app_id = str(item.get('AppID', '')).strip()
                if not app_id:
                    continue
                if needle == name:
                    exact = app_id
                    break
                if needle in name and partial is None:
                    partial = app_id
            return exact or partial
        except Exception:
            return None

    def _get_start_apps(self):
        if self.start_apps_cache is not None:
            return self.start_apps_cache
        completed = subprocess.run(
            [
                'powershell.exe',
                '-NoProfile',
                '-Command',
                'Get-StartApps | Select-Object Name,AppID | ConvertTo-Json -Compress',
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if completed.returncode != 0 or not completed.stdout.strip():
            self.start_apps_cache = []
            return self.start_apps_cache
        data = json.loads(completed.stdout)
        if isinstance(data, dict):
            data = [data]
        self.start_apps_cache = data
        return self.start_apps_cache

    def _send_whatsapp(self, query):
        text = query.strip()
        lower = text.lower()
        for prefix in ('send whatsapp ', 'whatsapp '):
            if lower.startswith(prefix):
                text = text[len(prefix):].strip()
                break

        phone = ''
        message = ''
        if ':' in text:
            phone, message = text.split(':', 1)
        elif ' message ' in text.lower():
            before, message = text.split(' message ', 1)
            phone = before.replace('to ', '', 1)
        elif ' to ' in text.lower():
            before, after = text.split(' to ', 1)
            phone = before.strip()
            message = after.strip()

        phone = ''.join(ch for ch in phone if ch.isdigit())
        message = message.strip()

        if not phone or not message:
            self.events.put(('reply', 'Use: whatsapp <country-code-phone>: <message>. Example: whatsapp 919876543210: hello'))
            return

        url = 'https://wa.me/' + phone + '?text=' + quote(message)
        webbrowser.open_new_tab(url)
        self.events.put(('reply', 'Prepared a WhatsApp message. Review it, then press Send in WhatsApp.'))

    def _warm_ollama(self):
        model = self.ollama_model_value
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': 'ok'}],
            'stream': False,
            'keep_alive': '10m',
            'options': {'num_predict': 1},
        }
        try:
            requests.post(OLLAMA_HOST + '/api/chat', json=payload, timeout=90)
            self.events.put(('note', 'Ollama model warmed: ' + model))
        except Exception:
            pass

    def _ollama_status(self):
        try:
            response = requests.get(OLLAMA_HOST + '/api/tags', timeout=4)
            response.raise_for_status()
            models = [item.get('name', '') for item in response.json().get('models', [])]
        except Exception:
            self.events.put(('reply', 'Ollama is not reachable. Start it with the Ollama app or run `ollama serve`.'))
            return

        if not models:
            self.events.put(('reply', 'Ollama is running, but no models are installed. Run `ollama pull ' + self.ollama_model_value + '`.'))
            return

        model = self.ollama_model_value
        if model in models:
            self.events.put(('reply', 'Ollama is ready with ' + model + '.'))
        else:
            self.events.put(('reply', 'Ollama is running. Installed models: ' + ', '.join(models) + '. Current UI model is ' + model + '.'))

    def _answer_with_web(self, prompt):
        if not prompt:
            self.events.put(('reply', 'Give me something to search for after web.'))
            return
        self.events.put(('note', 'Searching the live web...'))
        try:
            results = self._search_web(prompt)
        except Exception as exc:
            self.events.put(('reply', 'Live web search failed: ' + str(exc)))
            return

        if not results:
            self.events.put(('reply', 'I could not find live web results for that.'))
            return

        summary = self._summarize_web_results(prompt, results)
        sources = '\n\nSources:\n' + '\n'.join(
            str(index) + '. ' + result['title'] + ' - ' + result['url']
            for index, result in enumerate(results[:4], start=1)
        )
        self.events.put(('reply', summary + sources))

    def _search_web(self, query):
        response = requests.get(
            'https://duckduckgo.com/html/',
            params={'q': query},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=15,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for node in soup.select('.result')[:6]:
            link = node.select_one('.result__a')
            if link is None:
                continue
            title = link.get_text(' ', strip=True)
            href = self._clean_duckduckgo_url(link.get('href', ''))
            snippet_node = node.select_one('.result__snippet')
            snippet = snippet_node.get_text(' ', strip=True) if snippet_node else ''
            if title and href:
                results.append({'title': title, 'url': href, 'snippet': snippet})
        return results

    def _clean_duckduckgo_url(self, href):
        if href.startswith('//'):
            href = 'https:' + href
        parsed = urlparse(href)
        target = parse_qs(parsed.query).get('uddg', [''])[0]
        if target:
            return unquote(target)
        return href

    def _summarize_web_results(self, prompt, results):
        model = self.ollama_model_value
        context = '\n'.join(
            '[' + str(index) + '] ' + item['title'] + '\n'
            + item['snippet'] + '\n'
            + item['url']
            for index, item in enumerate(results[:5], start=1)
        )
        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        'You are AeroA.I. Answer using only the provided live web search snippets. '
                        'Be concise. If the snippets are insufficient, say what is missing. '
                        'Mention source numbers like [1] when useful.'
                    ),
                },
                {'role': 'user', 'content': 'Question: ' + prompt + '\n\nLive web snippets:\n' + context},
            ],
            'stream': False,
            'keep_alive': '10m',
            'options': {
                'temperature': 0.2,
                'num_predict': 220,
                'num_ctx': 4096,
            },
        }
        try:
            response = requests.post(OLLAMA_HOST + '/api/chat', json=payload, timeout=120)
            response.raise_for_status()
            answer = response.json().get('message', {}).get('content', '').strip()
            if answer:
                return answer
        except Exception:
            pass

        lines = ['Here are the freshest results I found:']
        for index, item in enumerate(results[:4], start=1):
            detail = item['snippet'] or item['url']
            lines.append('[' + str(index) + '] ' + item['title'] + ': ' + detail)
        return '\n'.join(lines)

    def _ask_ollama(self, prompt):
        model = self.ollama_model_value
        self.events.put(('note', 'Thinking with Ollama (' + model + ')...'))
        options = {
            'temperature': 0.3,
        }
        if self.fast_replies_value:
            options.update({
                'num_predict': 160,
                'num_ctx': 2048,
                'top_k': 30,
                'top_p': 0.85,
            })
        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are AeroA.I, a concise helpful desktop assistant. Keep answers short unless asked for detail.',
                },
                {'role': 'user', 'content': prompt},
            ],
            'stream': False,
            'keep_alive': '10m',
            'options': options,
        }
        try:
            response = requests.post(OLLAMA_HOST + '/api/chat', json=payload, timeout=120)
            response.raise_for_status()
            answer = response.json().get('message', {}).get('content', '').strip()
        except requests.exceptions.ConnectionError:
            self.events.put(('reply', 'Ollama is not running. Open the Ollama app or run `ollama serve`, then try again.'))
            return
        except requests.exceptions.HTTPError as exc:
            body = exc.response.text if exc.response is not None else ''
            if 'not found' in body.lower() or 'pull' in body.lower():
                self.events.put(('reply', 'That Ollama model is not installed. Run `ollama pull ' + model + '` and try again.'))
            else:
                self.events.put(('reply', 'Ollama returned an error: ' + body[:300]))
            return
        except Exception as exc:
            self.events.put(('reply', 'Ollama request failed: ' + str(exc)))
            return

        if answer:
            self.events.put(('reply', answer))
        else:
            self.events.put(('reply', 'Ollama returned an empty response.'))

    def _wikipedia(self, topic):
        if not topic:
            self.events.put(('reply', 'Give me a topic after wikipedia.'))
            return
        if wikipedia is None:
            webbrowser.open_new_tab('https://google.com/search?q=' + quote_plus(topic))
            self.events.put(('reply', 'Wikipedia package is not available, so I opened a web search.'))
            return
        try:
            summary = wikipedia.summary(topic, sentences=2)
            self.events.put(('reply', summary))
        except Exception:
            webbrowser.open_new_tab('https://google.com/search?q=' + quote_plus(topic))
            self.events.put(('reply', 'I could not fetch that summary, so I opened a web search.'))

    def _news(self):
        url = getNewsUrl()
        if 'newsapi.org' not in url:
            webbrowser.open_new_tab(url)
            self.events.put(('reply', 'NEWS_API_KEY is not configured, so I opened Google News.'))
            return
        speak_news()
        self.events.put(('reply', 'Read the latest configured headlines.'))

    def start_voice_assistant(self):
        python_exe = BASE_DIR / '.venv' / 'Scripts' / 'python.exe'
        if not python_exe.exists():
            python_exe = Path(sys.executable)
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NEW_CONSOLE
        subprocess.Popen(
            [str(python_exe), str(BASE_DIR / 'aero.py'), '--no-auth'],
            cwd=str(BASE_DIR),
            creationflags=creationflags,
        )
        self.reply('Started the voice assistant in a new console window.')

    def _drain_events(self):
        while True:
            try:
                kind, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == 'reply':
                self.reply(payload)
            elif kind == 'note':
                self.note(payload)
            elif kind == 'heard':
                self.handle_command(payload)
            elif kind == 'start_voice':
                self.start_voice_assistant()
            elif kind == 'close':
                self.after(700, self.destroy)
        self.after(120, self._drain_events)


if __name__ == '__main__':
    AeroUI().mainloop()
