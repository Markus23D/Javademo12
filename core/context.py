class Context:
    def __init__(self):
        self.last_app = None
        self.last_action = None
        self.last_query = None
        self.last_command = None

    def update(self, key, value):
        setattr(self, key, value)

    def get(self, key):
        return getattr(self, key, None)


context = Context()