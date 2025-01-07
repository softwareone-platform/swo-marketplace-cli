class State:
    """Global state for the CLI"""
    def __init__(self):
        self.verbose = False

state = State()

__all__ = ['state']
