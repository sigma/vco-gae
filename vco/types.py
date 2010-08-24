from generated.VSOWebControlService_types import *
from ZSI.schema import GTD

__schema = "http://webservice.vso.dunes.ch"

def __getClass(name):
    return GTD(__schema, name)(name).pyclass

Property = __getClass("Property")
ArrayOfProperty = __getClass("ArrayOfProperty")
FinderResult = __getClass("FinderResult")
ArrayOfFinderResult = __getClass("ArrayOfFinderResult")
QueryResult = __getClass("QueryResult")
WorkflowParameter = __getClass("WorkflowParameter")
ArrayOfWorkflowParameter = __getClass("ArrayOfWorkflowParameter")
Workflow = __getClass("Workflow")
WorkflowTokenAttribute = __getClass("WorkflowTokenAttribute")
WorkflowToken = __getClass("WorkflowToken")
ModuleInfo = __getClass("ModuleInfo")
