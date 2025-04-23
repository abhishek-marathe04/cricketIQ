class AmbiguousPlayerNameError(Exception):
    def __init__(self, message="Player name is ambiguous. Please be more specific."):
        self.message = message
        super().__init__(self.message)

class NoPlayerFoundError(Exception):
    def __init__(self, message="Player not found"):
        self.message = message
        super().__init__(self.message)