class States:
    @staticmethod
    def startState(rights):
        pass


class StateMachine:
    def __init__(self):
        self.states = [0]

    def currentState(self):
        return self.states[-1]

    def walk(self, state):
        self.states.append(state)

    def back(self):
        self.states.pop(-1)
        return self.currentState()

    def toStart(self):
        self.states.clear()
        return 0
