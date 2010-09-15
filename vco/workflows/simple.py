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
        completed.setResults(out=inputs['in'][1])

        db.put([running,completed])

class Wait(WorkflowImplementationBase):

    def __init__(self):
        self._delay = timedelta(seconds=5)
        self._timeout = timedelta(hours=1)

    def initTokens(self, token, inputs):
        wait = datetime.now() + self._delay
        timeout = wait + self._timeout

        running, waiting, timedout = token.split(wait, timeout)

        waiting.setWaiting()

        timedout.setFailed()

        db.put([running, waiting, timedout])

    def updateTokens(self, token, inputs):
        end = datetime.now() + self._delay
        running, completed = token.merge().split(end)

        running.setRunning()

        completed.setCompleted()
        completed.setResults()

        db.put([running, completed])
