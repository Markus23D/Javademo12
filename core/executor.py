import json
import time
import webbrowser
import pyautogui
import os
import subprocess
from urllib.parse import quote_plus
import pygetwindow as gw


class Executor:

    def __init__(self, context=None):
        self.context = context

        base_dir = os.path.dirname(os.path.dirname(__file__))
        apps_path = os.path.join(base_dir, "commands.json")

        with open(apps_path, "r", encoding="utf-8") as f:
            self.apps = json.load(f)

        self.actions = {
            "wait": self.wait,
            "open_url": self.open_url,
            "open_app": self.open_app,
            "youtube_search": self.youtube_search,
            "spotify_search": self.spotify_search,
            "play_song": self.play_song,
            "play_youtube": self.play_youtube,
            "type": self.type_text,
            "shutdown": self.shutdown,
            "restart": self.restart,
            "standby": self.standby,
            "speak": self.speak_action,
            "scroll": self.scroll,
            "hotkey": self.hotkey,
            "click": self.click,
            "active_window": self.active_window,
            "switch_window": self.switch_window,
            "switch_back": self.switch_back,
            "repeat_last_search": self.repeat_last_search,
            "list_windows": self.list_windows,
            "volume": self.volume,
            "media":  self.media,
        }

    def execute(self, plan):
        for step in plan:
            action = step.get("action")
            value = step.get("value")

            func = self.actions.get(action)

            if not func:
                print(f"[UNKNOWN ACTION] {action}")
                from voice.tts import speak
                speak("I don't know how to do that sir")
                continue

            func(value)

    def get_media_query(self, value):
        if isinstance(value, dict):
            song = value.get("song", "")
            artist = value.get("artist")

            if artist:
                return f"{song} {artist}".strip()

            return song.strip()

        return str(value).strip()

    def open_app(self, value):
        key = value.lower().strip().rstrip(".!?,;")
        matched = None

        for app_name, data in self.apps.items():
            aliases = [a.lower() for a in data.get("aliases", [])]

            if key == app_name.lower() or key in aliases:
                matched = data
                break

        if not matched:
            print(f"[APP NOT FOUND] {value}")
            from voice.tts import speak
            speak(f"I don't know how to open {value} sir")
            return

        # Web-type entries open a URL in the browser
        if matched.get("type") == "web":
            url = matched.get("url")
            if url:
                print(f"[OPENING URL] {url}")
                webbrowser.open(url)
                if self.context:
                    self.context.set_active_app(value)
            return

        # App-type entries launch an executable
        path = os.path.expandvars(matched.get("path", ""))
        if not path:
            print(f"[APP NO PATH] {value}")
            return

        print("[LAUNCHING]", path)

        try:
            if path.endswith(":"):
                os.startfile(path)
            else:
                subprocess.Popen(path, shell=True)

            if self.context:
                self.context.set_active_app(value)

        except Exception as e:
            print(f"[ERROR OPENING APP] {value}: {e}")
            from voice.tts import speak
            speak(f"I had trouble opening {value} sir")

    def open_url(self, value):
        webbrowser.open(value)

        if self.context:
            if "youtube.com/results?search_query=" in value:
                query = value.split("search_query=", 1)[1].replace("+", " ")
                self.context.set_search("youtube", query)

            elif "google.com/search?q=" in value:
                query = value.split("q=", 1)[1].replace("+", " ")
                self.context.set_search("google", query)

            elif value.startswith("spotify:search:"):
                query = value.replace("spotify:search:", "", 1)
                query = query.replace("%20", " ")
                self.context.set_search("spotify", query)

    def youtube_search(self, value):
        query = self.get_media_query(value)

        url = f"https://youtube.com/results?search_query={quote_plus(query)}"
        webbrowser.open(url)

        if self.context:
            self.context.set_search("youtube", query)

    def spotify_search(self, value):
        query = self.get_media_query(value)

        print(f"[SPOTIFY SEARCH] {query}")

        os.startfile(f"spotify:search:{quote_plus(query)}")
        time.sleep(2)

        if self.context:
            self.context.set_search("spotify", query)

    def play_song(self, value):
        query = self.get_media_query(value)

        print(f"[PLAY SPOTIFY] {query}")

        os.startfile(f"spotify:search:{quote_plus(query)}")
        time.sleep(3)

        # Use keyboard navigation instead of hardcoded pixel coords
        pyautogui.press("tab")
        time.sleep(0.3)
        pyautogui.press("enter")

        if self.context:
            self.context.set_search("spotify", query)

    def play_youtube(self, value):
        query = self.get_media_query(value)

        print(f"[PLAY YOUTUBE] {query}")

        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        webbrowser.open(url)

        time.sleep(5)

        # Use keyboard navigation instead of hardcoded pixel coords
        pyautogui.press("tab")
        time.sleep(0.3)
        pyautogui.press("enter")

        if self.context:
            self.context.set_search("youtube", query)

    def type_text(self, value):
        pyautogui.write(value or "", interval=0.02)

    def wait(self, value):
        time.sleep(value or 1)

    def shutdown(self, value=None):
        os.system("shutdown /s /t 5")

    def restart(self, value=None):
        os.system("shutdown /r /t 5")

    def standby(self, value=None):
        print("[EXECUTOR] standby handled by UI")

    def speak_action(self, value):
        from voice.tts import speak
        print("[SPEAK ACTION]", value)
        speak(value or "")

    def scroll(self, value):
        pyautogui.scroll(value or 0)

    def hotkey(self, value):
        if isinstance(value, list):
            pyautogui.hotkey(*value)

    def click(self, value=None):
        pyautogui.click()

    def active_window(self, value=None):
        window = gw.getActiveWindow()

        if not window:
            print("[ACTIVE WINDOW] Unknown")
            return

        print(f"[ACTIVE WINDOW] {window.title}")

    def switch_window(self, value):
        target = value.lower().strip()
        windows = gw.getAllWindows()

        # Extra aliases for apps whose window titles don't match their common name
        aliases = {
            "discord":  ["discord"],
            "spotify":  ["spotify", "spotify premium"],
            "chrome":   ["chrome", "google chrome"],
            "overwolf": ["overwolf"],
            "vs code":  ["visual studio code", "vscode"],
            "vscode":   ["visual studio code", "vscode"],
            "explorer": ["file explorer", "windows explorer", "this pc"],
        }

        search_terms = aliases.get(target, [target])

        # First pass — exact substring match
        match = self._find_window(windows, search_terms)

        # Second pass — fuzzy: any search term appears anywhere in the title
        if not match:
            match = self._find_window(windows, search_terms, fuzzy=True)

        if match:
            try:
                if match.isMinimized:
                    match.restore()

                match.activate()
                time.sleep(0.2)

                x = match.left + match.width // 2
                y = match.top + match.height // 2
                pyautogui.click(x, y)

                print(f"[SWITCHED WINDOW] {match.title}")

                if self.context:
                    self.context.set_active_app(target)

            except Exception as e:
                print("[SWITCH ERROR]", e)
                from voice.tts import speak
                speak(f"I couldn't switch to {value} sir")
        else:
            print(f"[WINDOW NOT FOUND] {target}")
            from voice.tts import speak
            speak(f"I can't find {value} sir, is it open?")

    def _find_window(self, windows, search_terms, fuzzy=False):
        for window in windows:
            if not window.title:
                continue
            title = window.title.lower()
            if fuzzy:
                if any(term in title or title in term for term in search_terms):
                    return window
            else:
                if any(term in title for term in search_terms):
                    return window
        return None

    def repeat_last_search(self, value=None):
        if not self.context:
            print("[NO CONTEXT]")
            return

        last = getattr(self.context, "last_search", None)

        if not last:
            print("[NO LAST SEARCH]")
            return

        engine = getattr(self.context, "last_search_engine", "google")

        if engine == "youtube":
            self.youtube_search(last)

        elif engine == "spotify":
            self.spotify_search(last)

        else:
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(last)}")

    def switch_back(self, value=None):
        if not self.context:
            print("[NO CONTEXT]")
            return

        previous = self.context.previous_app

        if not previous:
            print("[NO PREVIOUS APP]")
            return

        self.switch_window(previous)

    def media(self, value):
        pyautogui.press(value)

    def volume(self, value):
        key = value.get("key", "volumeup")
        presses = value.get("presses", 5)
        for _ in range(presses):
            pyautogui.press(key)

    def list_windows(self, value=None):
        windows = gw.getAllWindows()

        print("[OPEN WINDOWS]")

        for window in windows:
            if window.title:
                print("-", window.title)