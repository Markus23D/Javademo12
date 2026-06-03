import json
import time
import webbrowser
import pyautogui
import os
import subprocess
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
        }

    def execute(self, plan):
        for step in plan:
            action = step.get("action")
            value = step.get("value")

            func = self.actions.get(action)

            if not func:
                print(f"[UNKNOWN ACTION] {action}")
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
        key = value.lower().strip()
        path = None

        for app_name, data in self.apps.items():
            aliases = [a.lower() for a in data.get("aliases", [])]

            if key == app_name.lower() or key in aliases:
                path = os.path.expandvars(data.get("path"))
                break

        if not path:
            print(f"[APP NOT FOUND] {value}")
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

        url = f"https://youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)

        if self.context:
            self.context.set_search("youtube", query)

    def spotify_search(self, value):
        query = self.get_media_query(value)

        print(f"[SPOTIFY SEARCH] {query}")

        os.startfile(f"spotify:search:{query.replace(' ', '%20')}")
        time.sleep(2)

        if self.context:
            self.context.set_search("spotify", query)

    def play_song(self, value):
        query = self.get_media_query(value)

        print(f"[PLAY SPOTIFY] {query}")

        os.startfile(f"spotify:search:{query.replace(' ', '%20')}")
        time.sleep(3)

        pyautogui.click(470, 390)
        time.sleep(0.5)

        pyautogui.press("enter")

        if self.context:
            self.context.set_search("spotify", query)

    def play_youtube(self, value):
        query = self.get_media_query(value)

        print(f"[PLAY YOUTUBE] {query}")

        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)

        time.sleep(5)

        pyautogui.click(620, 360)

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
        print("[SPEAK ACTION]", value)

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

        aliases = {
            "discord": ["discord"],
            "spotify": ["spotify", "spotify premium"],
            "chrome": ["chrome", "google chrome"],
            "overwolf": ["overwolf"],
        }

        search_terms = aliases.get(target, [target])

        for window in windows:
            if not window.title:
                continue

            title = window.title.lower()

            if any(term in title for term in search_terms):
                try:
                    if window.isMinimized:
                        window.restore()

                    window.activate()
                    time.sleep(0.2)

                    x = window.left + window.width // 2
                    y = window.top + window.height // 2
                    pyautogui.click(x, y)

                    print(f"[SWITCHED WINDOW] {window.title}")

                    if self.context:
                        self.context.set_active_app(target)

                    return

                except Exception as e:
                    print("[SWITCH ERROR]", e)
                    return

        print(f"[WINDOW NOT FOUND] {target}")

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
            webbrowser.open(f"https://www.google.com/search?q={last.replace(' ', '+')}")

    def switch_back(self, value=None):
        if not self.context:
            print("[NO CONTEXT]")
            return

        previous = self.context.previous_app

        if not previous:
            print("[NO PREVIOUS APP]")
            return

        self.switch_window(previous)

    def list_windows(self, value=None):
        windows = gw.getAllWindows()

        print("[OPEN WINDOWS]")

        for window in windows:
            if window.title:
                print("-", window.title)