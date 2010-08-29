from _base import WorkflowImplementationBase
from datetime import timedelta, datetime
from google.appengine.ext import db

class Sleep(WorkflowImplementationBase):

    def __init__(self):
        self._delay = timedelta(seconds=10)

    def initTokens(self, token, inputs):
        end = datetime.now() + self._delay

        running, completed = token.split(end)

        completed.setCompleted()
        completed.setResults({'out': inputs['in'][1]})

        db.put([running,completed])

class Wait(WorkflowImplementationBase):

    def __init__(self):
        self._delay = timedelta(seconds=5)

    def initTokens(self, token, inputs):
        wait = datetime.now() + self._delay

        running, waiting = token.split(wait)

        waiting.setWaiting()

        db.put([running, waiting])

    def updateTokens(self, token, inputs):
        end = datetime.now() + self._delay
        running, completed = token.split(end)

        running.setRunning()

        completed.setCompleted()
        completed.setResults({})

        db.put([running, completed])
