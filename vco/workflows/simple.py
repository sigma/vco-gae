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
