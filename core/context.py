class Context:

    def __init__(self):

        self.last_app = None
        self.last_command = None

        self.history = []

    def remember(self, command):

        self.last_command = command

        self.history.append(command)

        if len(self.history) > 50:
            self.history.pop(0)


context = Context()