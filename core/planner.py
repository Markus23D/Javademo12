class Planner:

    SEPARATORS = [" and ", " then ", ","]

    @classmethod
    def split_command(cls, text):
        text = text.lower().strip()

        if text.startswith("open ") and " search " in text and " and " not in text:
            text = text.replace(" search ", " and search ", 1)

        commands = [text]

        for sep in cls.SEPARATORS:
            new_commands = []

            for cmd in commands:
                new_commands.extend(cmd.split(sep))

            commands = new_commands

        return [c.strip() for c in commands if c.strip()]

    @classmethod
    def google_search_url(cls, query):
        return f"https://www.google.com/search?q={query.replace(' ', '+')}"

    @classmethod
    def build_plan(cls, text):
        steps = []

        for part in cls.split_command(text):
            part = part.lower().strip()

            if part.startswith("type "):
                steps.append({
                    "action": "type",
                    "value": part.replace("type ", "", 1).strip()
                })

            elif part.startswith("play "):
                query = part.replace("play ", "", 1).strip()
                platform = "spotify"

                if query.endswith(" on youtube"):
                    platform = "youtube"
                    query = query.replace(" on youtube", "", 1).strip()

                elif query.endswith(" on spotify"):
                    platform = "spotify"
                    query = query.replace(" on spotify", "", 1).strip()

                if " by " in query:
                    song, artist = query.split(" by ", 1)
                    value = {
                        "song": song.strip(),
                        "artist": artist.strip()
                    }
                else:
                    value = {
                        "song": query,
                        "artist": None
                    }

                if platform == "youtube":
                    steps.append({
                        "action": "play_youtube",
                        "value": value
                    })
                else:
                    steps.append({
                        "action": "play_song",
                        "value": value
                    })

            elif part.startswith("search youtube for "):
                query = part.replace("search youtube for ", "", 1).strip()
                steps.append({
                    "action": "youtube_search",
                    "value": query
                })

            elif part.startswith("search youtube "):
                query = part.replace("search youtube ", "", 1).strip()
                steps.append({
                    "action": "youtube_search",
                    "value": query
                })

            elif part.startswith("youtube "):
                query = part.replace("youtube ", "", 1).strip()
                steps.append({
                    "action": "youtube_search",
                    "value": query
                })

            elif part.startswith("search spotify for "):
                query = part.replace("search spotify for ", "", 1).strip()
                steps.append({
                    "action": "spotify_search",
                    "value": query
                })

            elif part.startswith("search spotify "):
                query = part.replace("search spotify ", "", 1).strip()
                steps.append({
                    "action": "spotify_search",
                    "value": query
                })

            elif part.startswith("spotify "):
                query = part.replace("spotify ", "", 1).strip()
                steps.append({
                    "action": "spotify_search",
                    "value": query
                })

            elif part.startswith("search google for "):
                query = part.replace("search google for ", "", 1).strip()
                steps.append({
                    "action": "open_url",
                    "value": cls.google_search_url(query)
                })

            elif part.startswith("search google "):
                query = part.replace("search google ", "", 1).strip()
                steps.append({
                    "action": "open_url",
                    "value": cls.google_search_url(query)
                })

            elif part.startswith("google "):
                query = part.replace("google ", "", 1).strip()
                steps.append({
                    "action": "open_url",
                    "value": cls.google_search_url(query)
                })

            elif part in ["youtube", "you too", "you tube", "open youtube"]:
                steps.append({
                    "action": "open_url",
                    "value": "https://youtube.com"
                })

            elif part.startswith("search ") or part.startswith("look up "):
                query = part

                for prefix in ["search ", "look up "]:
                    if query.startswith(prefix):
                        query = query.replace(prefix, "", 1).strip()

                if query.startswith("for "):
                    query = query.replace("for ", "", 1).strip()

                steps.append({
                    "action": "open_url",
                    "value": cls.google_search_url(query)
                })

            elif part in ["open google", "google"]:
                steps.append({
                    "action": "open_url",
                    "value": "https://google.com"
                })

            elif part in ["open facebook", "facebook"]:
                steps.append({
                    "action": "open_url",
                    "value": "https://facebook.com"
                })

            elif part in ["open github", "github"]:
                steps.append({
                    "action": "open_url",
                    "value": "https://github.com"
                })

            elif part in ["open netflix", "netflix"]:
                steps.append({
                    "action": "open_url",
                    "value": "https://netflix.com"
                })

            elif part.startswith("open "):
                app = part.replace("open ", "", 1).strip()

                steps.append({
                    "action": "open_app",
                    "value": app
                })

            elif part in ["standby", "stand by", "sleep", "go idle", "go to sleep"]:
                steps.append({
                    "action": "standby",
                    "value": None
                })

            elif part == "shutdown":
                steps.append({
                    "action": "shutdown",
                    "value": None
                })

            elif part == "restart":
                steps.append({
                    "action": "restart",
                    "value": None
                })

            else:
                pass

            return steps