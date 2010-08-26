from _base import WorkflowImplementationBase
from datetime import timedelta

class Sleep(WorkflowImplementationBase):

    def __init__(self):
        self._delay = timedelta(seconds=10)

    def initToken(self, tok):
        pass
