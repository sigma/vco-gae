from _base import WorkflowImplementationBase
from datetime import timedelta, datetime
from google.appengine.ext import db

class Sleep(WorkflowImplementationBase):

    def __init__(self):
        self._delay = timedelta(seconds=10)

    def initTokens(self, token, inputs):
        end = datetime.now()+self._delay

        end_token = token.clone(end=end)
        end_token.complete()
        end_token.setResults({'out': inputs['in'][1]})

        token.invalidateAfter(end)

        db.put([token,end_token])
