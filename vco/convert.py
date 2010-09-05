import logging
from types import *
from google.appengine.ext import db

def convertPlugin(plug, target=None):
    if target is None:
        target = ModuleInfo()
    target._moduleName = plug.name
    target._moduleVersion = plug.version
    target._moduleDisplayName = plug.display
    target._moduleDescription = plug.description
    return target

def convertParameter(param):
    param = db.get(param)
    p = WorkflowParameter()
    p._name = param.name
    p._type = param.type
    return p

def convertParameters(params):
    ps = ArrayOfWorkflowParameter()
    ps._item = [convertParameter(p)
                for p in params]
    return ps

def convertWorkflow(wf, target=None):
    if target is None:
        target = Workflow()
    target._id = wf.id
    target._name = wf.name
    target._description = wf.description
    target._inParameters = convertParameters(wf.input)
    target._outParameters = convertParameters(wf.output)
    target._attributes = convertParameters(wf.attributes)
    return target

def convertWorkflowToken(tok, target=None):
    if target is None:
        target = WorkflowToken()
    target._id = tok.id
    target._title = tok.title
    target._workflowId = tok.wf.id
    target._currentItemName = tok.cur_name
    target._currentItemState = tok.cur_state
    target._globalState = tok.state
    target._startDate = "%s" % (tok.start)
    target._endDate = "%s" % (tok.end)
    target._xmlContent = tok.xml
    return target

def convertWorkflowTokenResult(tok):
    res = []
    outputs = tok.wf.output
    results = tok.getResults()
    for out, idx in zip(outputs, range(len(outputs))):
        attr = WorkflowTokenAttribute()
        out = db.get(out)
        attr._name = out.name
        attr._type = out.type
        attr._value = results.get(attr._name, "")
        res.append(attr)
    return res
