class BadStateError(Exception):
    def __init__(self, required_state, current_state):
        self.required_state= required_state
        self.current_state = current_state