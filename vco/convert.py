import logging
from types import *
from google.appengine.ext import db

class PluginConverter(object):

    @staticmethod
    def toJSON(plug):
        json = {'name': plug.name,
                'version': plug.version,
                'display': plug.display,
                'description': plug.description}
        return json

    @staticmethod
    def toSOAP(json):
        soap = ModuleInfo()
        soap._moduleName = json['name']
        soap._moduleVersion = json['version']
        soap._moduleDisplayName = json['display']
        soap._moduleDescription = json['description']
        return soap

class ParameterConverter(object):

    @staticmethod
    def toJSON(param):
        param = db.get(param)
        json = {'name': param.name,
                'type': param.type}
        return json

    @staticmethod
    def toSOAP(json):
        soap = WorkflowParameter()
        soap._name = json['name']
        soap._type = json['type']
        return soap

class ParametersConverter(object):

    @staticmethod
    def toJSON(params):
        json = {'items': [ParameterConverter.toJSON(p) for p in params]}
        return json

    @staticmethod
    def toSOAP(json):
        soap = ArrayOfWorkflowParameter()
        soap._item = [ParameterConverter.toSOAP(j) for j in json['items']]
        return soap

class WorkflowConverter(object):

    @staticmethod
    def toJSON(wf):
        json = {'id': wf.id,
                'name': wf.name,
                'description': wf.description,
                'input': ParametersConverter.toJSON(wf.input),
                'output': ParametersConverter.toJSON(wf.output),
                'attributes': ParametersConverter.toJSON(wf.attributes)}
        return json

    @staticmethod
    def toSOAP(json):
        soap = Workflow()
        soap._id = json['id']
        soap._name = json['name']
        soap._description = json['description']
        soap._inParameters = ParametersConverter.toSOAP(json['input'])
        soap._outParameters = ParametersConverter.toSOAP(json['output'])
        soap._attributes = ParametersConverter.toSOAP(json['attributes'])
        return soap

class WorkflowTokenConverter(object):

    @staticmethod
    def toJSON(tok):
        json = {'id': tok.id,
                'title': tok.title,
                'wf_id': tok.wf.id,
                'cur_name': tok.cur_name,
                'cur_state': tok.cur_state,
                'state': tok.state,
                'start': tok.start,
                'end': tok.end,
                'xml': tok.xml}
        return json

    @staticmethod
    def toSOAP(json):
        soap = WorkflowToken()
        soap._id = json['id']
        soap._title = json['title']
        soap._workflowId = json['wf_id']
        soap._currentItemName = json['cur_name']
        soap._currentItemState = json['cur_state']
        soap._globalState = json['state']
        soap._startDate = "%s" % (json['start'])
        if json['end'] is not None:
            soap._endDate = "%s" % (json['end'])
        soap._xmlContent = json['xml']
        return soap

class PluginObjectConverter(object):

    @staticmethod
    def toJSON(obj):
        obj_id = obj.obj_id
        obj_type = "%s:%s" % (obj.plugin.name, obj.type)
        json = {'type': obj_type,
                'id': obj_id,
                'uri': "dunes://service.dunes.ch/CustomSDKObject?id='%s'&dunesName='%s'" % (obj_id, obj_type),
                'props': obj.getProperties()}
        return json

    @staticmethod
    def toSOAP(json):
        soap = FinderResult()
        soap._type = json['type']
        soap._id = json['id']
        soap._dunesURI = json['uri']

        _props = ArrayOfProperty()
        properties = json['props']
        items = []
        for k,v in properties.items():
            p = Property()
            p._name = k
            p._value = v
            items.append(p)
        _props._item = items

        soap._properties = _props
        return soap

def convertQueryResult(items):
    target = QueryResult()
    target._totalCount = len(items)
    _res = ArrayOfFinderResult()
    _res._item = items
    target._elements = _res
    return target

def convertWorkflowTokenResult(tok):
    res = []
    outputs = tok.wf.output
    results = tok.getResults()
    for out in outputs:
        attr = WorkflowTokenAttribute()
        out = db.get(out)
        attr._name = out.name
        attr._type = out.type
        attr._value = results.get(attr._name, "")
        res.append(attr)
    return res
