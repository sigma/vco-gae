# Run this in admin console to populate the datastore

from vco.models import Plugin, Workflow, Parameter, WorkflowToken
from uuid import uuid1 as _uuid

from google.appengine.ext import db

# Cleanup everything
def _cleanup(kind):
    db.delete(kind.all())

_cleanup(Plugin)
_cleanup(Parameter)
_cleanup(Workflow)
_cleanup(WorkflowToken)

# Create plug-ins
p = Plugin(name="dummy", version="0.1",
           description="Dummy plug-in", display="Dummy !")
db.put(p)

# Create workflows
i = Parameter(name="in", type="string")
o = Parameter(name="out", type="string")
db.put([i,o])

wf1 = Workflow(id=str(_uuid()),
               name="Dummy workflow",
               description="this workflow just does nothing",
               input = [i.key()],
               output = [o.key()],
               attributes=[],
               wf_implem="simple.sleep")

wf2 = Workflow(id=str(_uuid()),
               name="Waiting workflow",
               description="this workflow just waits",
               input=[],
               output=[],
               attributes=[],
               wf_implem="simple.wait")

db.put([wf1, wf2])
