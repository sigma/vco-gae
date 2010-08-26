from _base import WorkflowImplementationBase
from datetime import timedelta, datetime
from vco.models import clone_entity
from google.appengine.ext import db

class Sleep(WorkflowImplementationBase):

    def __init__(self):
        self._delay = timedelta(seconds=10)

    def initTokens(self, token, inputs):
        end = datetime.now()+self._delay
        end_token = clone_entity(token, state="completed",
                                 end=end)
        token.p_time_limit = end
        db.put([token,end_token])
