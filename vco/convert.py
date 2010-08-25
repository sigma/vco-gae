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
