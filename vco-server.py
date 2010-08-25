import sys
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import vco.generated.VSOWebControlService_server
import vco.types as types
import vco.models as models
import vco.convert as convert

from ZSI.schema import GED
from ZSI.twisted.wsgi import SOAPApplication, soapmethod, SOAPHandlerChainFactory, WSGIApplication

def _soapmethod(op):
    op_request = GED("http://webservice.vso.dunes.ch", op).pyclass
    op_response = GED("http://webservice.vso.dunes.ch", op + "Response").pyclass
    return soapmethod(op_request.typecode, op_response.typecode,
                      operation=op, soapaction=op)

class VcoService(SOAPApplication):
    factory = SOAPHandlerChainFactory
    # wsdl_content = dict(name='Vco', targetNamespace='urn:echo',
    #                     imports=(), portType='')

    @_soapmethod('echo')
    def soap_echo(self, request, response, **kw):
        msg = request._message
        logging.debug("[/] echo: %s" % (msg))
        response._echoReturn = msg
        return request,response

    @_soapmethod('echoWorkflow')
    def soap_echoWorkflow(self, request, response, **kw):
        msg = request._workflowMessage
        logging.debug("[/] echo: %s" % (msg))
        response._echoWorkflowReturn = msg
        return request,response

    def __findWorkflow(self, wf_id=None, wf_name=None):
        query = models.Workflow.all()
        if wf_id is not None:
            query.filter('id =', wf_id)
            wf = query.get()
            if wf is not None:
                wf = convert.convertWorkflow(wf)
            return wf
        else:
            if wf_name is not None:
                query.filter('name =', wf_name)
            wfs = [convert.convertWorkflow(wf) for wf in query]
            return wfs

    @_soapmethod('getWorkflowForId')
    def soap_getWorkflowForId(self, request, response, **kw):
        wf_id = request._workflowId
        user = request._username
        pwd = request._password
        logging.debug("[%s/%s] getWorkflowForId: %s" % (user, pwd, wf_id))

        wf = self.__findWorkflow(wf_id=wf_id)
        response._getWorkflowForIdReturn = wf
        return request, response

    # TODO: complete implem
    @_soapmethod('executeWorkflow')
    def soap_executeWorkflow(self, request, response, **kw):
        wf_id = request._workflowId
        user = request._username
        pwd = request._password
        inputs = {}
        logging.debug("[%s/%s] executeWorkflow: %s (%s)" % (user, pwd, wf_id, inputs))
        for i in request._workflowInputs:
            inputs[i._name] = (i._type, i._value)

        response._executeWorkflowReturn = None
        return request, response

    # TODO: complete implem
    @_soapmethod('simpleExecuteWorkflow')
    def soap_simpleExecuteWorkflow(self, request, response, **kw):
        wf_id = request._in0
        user = request._in1
        pwd = request._in2
        inputs = {}
        logging.debug("[%s/%s] simpleExecuteWorkflow: %s (%s)" % (user, pwd, wf_id, inputs))

        # unserializing of inputs. Probably this is very fragile
        input = request._in3.split(',')
        for (name, type, value) in zip(input[::3], input[1::3], input[2::3]):
            inputs[name] = (type, value)

        response._simpleExecuteWorkflowReturn = None
        return request, response

    # TODO: complete implem
    @_soapmethod('cancelWorkflow')
    def soap_cancelWorkflow(self, request, response, **kw):
        tk_id = request._workflowTokenId
        user = request._username
        pwd = request._password
        logging.debug("[%s/%s] cancelWorkflow: %s (%s)" % (user, pwd, wf_id))
        return request, response

    # TODO: complete implem
    @_soapmethod('answerWorkflowInput')
    def soap_answerWorkflowInput(self, request, response, **kw):
        tk_id = request._workflowTokenId
        user = request._username
        pwd = request._password
        inputs = {}
        for i in request._answerInputs:
            inputs[i._name] = (i._type, i._value)

        return request, response

    # TODO: complete implem
    @_soapmethod('getWorkflowTokenStatus')
    def soap_getWorkflowTokenStatus(self, request, response, **kw):
        tk_ids = request._workflowTokenIds
        user = request._username
        pwd = request._password

        response._getWorkflowTokenStatusReturn = []
        return request, response

    # TODO: complete implem
    @_soapmethod('getWorkflowTokenResult')
    def soap_getWorkflowTokenResult(self, request, response, **kw):
        tk_id = request._workflowTokenId
        user = request._username
        pwd = request._password

        response._getWorkflowTokenResultReturn = None
        return request, response

    # TODO: complete implem
    @_soapmethod('getWorkflowTokenForId')
    def soap_getWorkflowTokenForId(self, request, response, **kw):
        tk_id = request._workflowTokenId
        user = request._username
        pwd = request._password

        response._getWorkflowTokenForIdReturn = None
        return request, response

    @_soapmethod('getAllPlugins')
    def soap_getAllPlugins(self, request, response, **kw):
        user = request._username
        pwd = request._password

        response._getAllPluginsReturn = [convert.convertPlugin(p)
                                         for p in list(models.Plugin.all())]
        return request, response

    @_soapmethod('getAllWorkflows')
    def soap_getAllWorkflows(self, request, response, **kw):
        user = request._username
        pwd = request._password

        wfs = self.__findWorkflow()
        response._getAllWorkflowsReturn = wfs
        return request, response

    @_soapmethod('getWorkflowsWithName')
    def soap_getWorkflowsWithName(self, request, response, **kw):
        user = request._username
        pwd = request._password
        workflowName = request._workflowName
        logging.debug("[%s/%s] getWorkflowsWithName: %s" % (user, pwd, workflowName))

        wfs = self.__findWorkflow(wf_name=workflowName)
        response._getWorkflowsWithNameReturn = wfs
        return request, response

    # TODO: complete implem
    @_soapmethod('hasRights')
    def soap_hasRights(self, request, response, **kw):
        response.hasRightsReturn = False
        return request, response

    # TODO: complete implem
    @_soapmethod('sendCustomEvent')
    def soap_sendCustomEvent(self, request, response, **kw):
        return request, response

    # TODO: complete implem
    @_soapmethod('findForId')
    def soap_findForId(self, request, response, **kw):
        type = request._type
        id = request._id
        user = request._username
        pwd = request._password

        response._findForIdReturn = None
        return request, response

    # TODO: complete implem
    @_soapmethod('findRelation')
    def soap_findRelation(self, request, response, **kw):
        type = request._parentType
        id = request._parentId
        relation = request._relationName
        user = request._username
        pwd = request._password

        response._findRelationReturn = []
        return response

    # TODO: complete implem
    @_soapmethod('hasChildrenInRelation')
    def soap_hasChildrenInRelation(self, request, response, **kw):
        type = request._parentType
        id = request._parentId
        relation = request._relationName
        user = request._username
        pwd = request._password

        response._hasChildrenRelationReturn = False
        return request, response

    # TODO: complete implem
    @_soapmethod('find')
    def soap_find(self, request, response, **kw):
        type = request._parentType
        id = request._parentId
        relation = request._relationName
        user = request._username
        pwd = request._password

        response._findReturn = []
        return response

application = WSGIApplication()
application['webservice'] = VcoService()

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
