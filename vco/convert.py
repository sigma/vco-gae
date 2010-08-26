from types import *
from google.appengine.ext import db

def convertPlugin(plug):
    p = ModuleInfo()
    p._moduleName = plug.name
    p._moduleVersion = plug.version
    p._moduleDisplayName = plug.display
    p._moduleDescription = plug.description
    return p

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

def convertWorkflow(wf):
    w = Workflow()
    w._id = wf.id
    w._name = wf.name
    w._description = wf.description
    w._inParameters = convertParameters(wf.input)
    w._outParameters = convertParameters(wf.output)
    w._attributes = convertParameters(wf.attributes)
    return w

def convertWorkflowToken(tok):
    t = WorkflowToken()
    t._id = tok.id
    t._title = tok.title
    t._workflowId = db.get(tok.wf).id
    t._currentItemName = tok.cur_name
    t._currentItemState = tok.cur_state
    t._globalState = tok.global_state
    t._startDate = "%s" % (tok.start)
    t._endDate = "%s" % (tok.end)
    t._xmlContent = tok.xml
    return t
