import sys
sys.path.insert(0, 'zope.zip')
sys.path.insert(0, 'ZSI.zip')

import logging
from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import vco.generated.VSOWebControlService_server
import vco.data4 as data4

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

    @_soapmethod('getWorkflowForId')
    def soap_getWorkflowForId(self, request, response, **kw):
        wf_id = request._workflowId
        user = request._username
        pwd = request._password
        logging.debug("[%s/%s] getWorkflowForId: %s" % (user, pwd, wf_id))

        wf = data4.Workflow.findById(wf_id)
        response._getWorkflowForIdReturn = wf
        return request, response

    @_soapmethod('executeWorkflow')
    def soap_executeWorkflow(self, request, response, **kw):
        wf_id = request._workflowId
        user = request._username
        pwd = request._password
        inputs = {}
        logging.debug("[%s/%s] executeWorkflow: %s (%s)" % (user, pwd, wf_id, inputs))
        for i in request._workflowInputs:
            inputs[i._name] = (i._type, i._value)

        wf = data4.Workflow.findById(wf_id)
        response._executeWorkflowReturn = wf.run(inputs)
        return request, response

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

        wf = data4.Workflow.findById(wf_id)
        response._simpleExecuteWorkflowReturn = wf.run(inputs)
        return request, response

    @_soapmethod('cancelWorkflow')
    def soap_cancelWorkflow(self, request, response, **kw):
        tk_id = request._workflowTokenId
        user = request._username
        pwd = request._password
        logging.debug("[%s/%s] cancelWorkflow: %s" % (user, pwd, tk_id))

        data4.WorkflowToken.findById(tk_id).cancel()

        return request, response

    @_soapmethod('answerWorkflowInput')
    def soap_answerWorkflowInput(self, request, response, **kw):
        tk_id = request._workflowTokenId
        user = request._username
        pwd = request._password
        inputs = {}
        for i in request._answerInputs:
            inputs[i._name] = (i._type, i._value)

        data4.WorkflowToken.findById(tk_id).answer(inputs)

        return request, response

    @_soapmethod('getWorkflowTokenStatus')
    def soap_getWorkflowTokenStatus(self, request, response, **kw):
        tk_ids = request._workflowTokenIds
        user = request._username
        pwd = request._password

        tks = [data4.WorkflowToken.findById(tk_id) for tk_id in tk_ids]
        response._getWorkflowTokenStatusReturn = [tk._globalState for tk in tks]

        return request, response

    @_soapmethod('getWorkflowTokenResult')
    def soap_getWorkflowTokenResult(self, request, response, **kw):
        tk_id = request._workflowTokenId
        user = request._username
        pwd = request._password

        token = data4.WorkflowToken.findById(tk_id)
        response._getWorkflowTokenResultReturn = token.result()

        return request, response

    @_soapmethod('getWorkflowTokenForId')
    def soap_getWorkflowTokenForId(self, request, response, **kw):
        tk_id = request._workflowTokenId
        user = request._username
        pwd = request._password

        response._getWorkflowTokenForIdReturn = data4.WorkflowToken.findById(tk_id)
        return request, response

    @_soapmethod('getAllPlugins')
    def soap_getAllPlugins(self, request, response, **kw):
        user = request._username
        pwd = request._password

        response._getAllPluginsReturn = data4.Plugin.findAll()
        return request, response

    @_soapmethod('getAllWorkflows')
    def soap_getAllWorkflows(self, request, response, **kw):
        user = request._username
        pwd = request._password

        wfs = data4.Workflow.findAll()
        response._getAllWorkflowsReturn = wfs
        return request, response

    @_soapmethod('getWorkflowsWithName')
    def soap_getWorkflowsWithName(self, request, response, **kw):
        user = request._username
        pwd = request._password
        workflowName = request._workflowName
        logging.debug("[%s/%s] getWorkflowsWithName: %s" % (user, pwd, workflowName))

        wfs = data4.Workflow.findByName(workflowName)
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

    @_soapmethod('findForId')
    def soap_findForId(self, request, response, **kw):
        type = request._type
        id = request._id
        user = request._username
        pwd = request._password

        objs = data4.FinderResult.find(id=id, type=type)
        if len(objs) == 0:
            obj = None
        else:
            obj = objs[0]

        response._findForIdReturn = obj
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

    @_soapmethod('find')
    def soap_find(self, request, response, **kw):
        type = request._type
        query = request._query
        user = request._username
        pwd = request._password

        objs = data4.FinderResult.find(type=type, query=query, _query_result=True)
        response._findReturn = objs
        return request, response

application = WSGIApplication()
application['webservice'] = VcoService()

def real_main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

def profile_main():
    # This is the main function for profiling
    # We've renamed our original main() above to real_main()
    import cProfile, pstats, StringIO
    prof = cProfile.Profile()
    prof = prof.runctx("real_main()", globals(), locals())
    stream = StringIO.StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(80)  # 80 = how many to print
    # The rest is optional.
    stats.print_callees()
    stats.print_callers()
    # output to logs
    logging.info("Profile data:\n%s", stream.getvalue())

main = real_main

if __name__ == "__main__":
    main()
