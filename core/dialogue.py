class DialogueManager:
    def __init__(self):
        self.state = "active"
        self.pending_action = None

    def set_state(self, state):
        self.state = state

    def ask_confirmation(self, plan):
        self.pending_action = plan
        self.state = "confirming"

    def confirm(self):
        plan = self.pending_action
        self.pending_action = None
        self.state = "active"
        return plan

    def cancel(self):
        self.pending_action = None
        self.state = "active"