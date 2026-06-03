class DialogueManager:

    def __init__(self):
        self.state = "active"
        self.last_intent = None
        self.last_text = None

    def update(self, text, intent):
        self.last_text = text
        self.last_intent = intent

    def set_state(self, state):
        self.state = state