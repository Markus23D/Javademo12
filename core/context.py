class Context:

    def __init__(self):
        self.last_app = None
        self.previous_app = None

        self.last_command = None
        self.last_search = None
        self.last_search_engine = None

        self.history = []

    def remember(self, command: str):
        command = command.lower().strip()

        self.last_command = command
        self.history.append(command)

        if command.startswith("search youtube for "):
            self.last_search_engine = "youtube"
            self.last_search = command.replace("search youtube for ", "", 1).strip()

        elif command.startswith("search google for "):
            self.last_search_engine = "google"
            self.last_search = command.replace("search google for ", "", 1).strip()

        elif command.startswith("search spotify for "):
            self.last_search_engine = "spotify"
            self.last_search = command.replace("search spotify for ", "", 1).strip()

        elif command.startswith("search "):
            self.last_search_engine = self.last_search_engine or "google"
            self.last_search = command.replace("search ", "", 1).strip()

        elif command.startswith("google "):
            self.last_search_engine = "google"
            self.last_search = command.replace("google ", "", 1).strip()

        if len(self.history) > 50:
            self.history.pop(0)

    def set_active_app(self, app_name):
        self.previous_app = self.last_app
        self.last_app = app_name

    def set_search(self, engine, query):
        self.last_search_engine = engine
        self.last_search = query

    def recent(self, n=5):
        return self.history[-n:]