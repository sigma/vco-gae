from uuid import uuid1 as _uuid
from workflows import getWorkflowImplementation

from google.appengine.api import memcache

import types
import models
import convert
import logging
from datetime import datetime

class _Item(object):
    _model = None
    _converter = None

    def __init__(self, model):
        self._json = self._converter.toJSON(model)

    def _asTarget(self):
        return self._converter.toSOAP(self._json)

    @classmethod
    def findAllUri(cls):
        return "data4://all/%s" % (cls.__name__)

    @classmethod
    def findAll(cls):
        uri = cls.findAllUri()
        elems = memcache.get(uri)
        if elems is None:
            if issubclass(cls._model, models.TimedItem):
                query = cls._model.allValid()
            else:
                query = cls._model.all()
            elems = [x for x in query]

            if len(elems) != 0 and issubclass(cls._model, models.TimedItem):
                ttl = elems[0].ttl()
            else:
                ttl = 0

            elems = [cls(i) for i in elems]
            memcache.add(uri, elems, ttl)

        items = [i._asTarget() for i in elems]
        return items

class _IdItem(_Item):

    @classmethod
    def findByIdUri(cls, id):
        return "data4://id/%s/%s" % (cls.__name__, id)

    @classmethod
    def findById(cls, id):
        uri = cls.findByIdUri(id)
        item = memcache.get(uri)

        if item is None:
            if issubclass(cls._model, models.TimedItem):
                item = cls._model.getItem(id)
                ttl = item.ttl()
                item = cls(item)
                memcache.add(uri, item, ttl)
            else:
                query = cls._model.all()
                query.filter('id =', id)
                item = query.get()
                item = cls(item)
                memcache.add(uri, item)

        item = item._asTarget()
        return item

class Plugin(_Item):
    _model = models.Plugin
    _converter = convert.PluginConverter

    def __init__(self, model):
        _Item.__init__(self, model)

class Workflow(types.Workflow, _IdItem):
    _model = models.Workflow
    _converter = convert.WorkflowConverter

    @classmethod
    def findByNameUri(cls, name):
        return "data4://id/%s/%s" % (cls.__name__, name)

    @classmethod
    def findByName(cls, name):
        uri = cls.findByNameUri(name)
        elems = memcache.get(uri)
        if elems is None:
            query = cls._model.all()
            query.filter('name =', name)
            elems = [x for x in query]
            elems = [cls(i) for i in elems]
            memcache.add(uri, elems)

        items = [e._asTarget() for e in elems]
        return items

    def __init__(self, model):
        _IdItem.__init__(self, model)

    def run(self, inputs):
        wf = self.findById(self._id)
        tk_id = str(_uuid())
        token = models.WorkflowToken(id=tk_id,
                                     wf=wf)

        wf = getWorkflowImplementation(wf.wf_implem)
        token.put()
        wf.initTokens(token, inputs)
        return WorkflowToken(token)

class WorkflowToken(_IdItem):
    _model = models.WorkflowToken
    _converter = convert.WorkflowTokenConverter

    def __init__(self, model):
        _IdItem.__init__(self, model)

    def cancel(self):
        self.findById(self._id).cancel().put()

    def answer(self, inputs):
        token = self.findById(self._id)
        if token.state == models.WorkflowToken._WAITING:
            wf = token.wf

            wf = getWorkflowImplementation(wf.wf_implem)
            wf.updateTokens(token, inputs)

    def result(self):
        return convert.convertWorkflowTokenResult(self.findById(self._id))

class FinderResult(_IdItem):
    _model = models.PluginObject
    _converter = convert.PluginObjectConverter

    def __init__(self, model):
        _IdItem.__init__(self, model)

    @classmethod
    def findUri(cls, type, id, query):
        return "data4://finder/%s/%s/%s" % (type, id, query)

    @classmethod
    def find(cls, type, id=None, query=None, _query_result=False):
        uri = cls.findUri(type, id, query)
        elems = memcache.get(uri)
        if elems is None:
            plugin, type = type.split(':')
            plugin = models.Plugin.all().filter('name =', plugin).get()

            query = cls._model.allValid()
            query.filter('plugin =', plugin)
            query.filter('type =', type)
            if id is not None:
                query.filter('obj_id =', id)
            elems = [x for x in query]

            if len(elems) != 0:
                now = datetime.now()
                ttl = elems[0].ttl()
            else:
                ttl = 0
            elems = [cls(e) for e in elems]
            memcache.add(uri, elems, ttl)

        items = [e._asTarget() for e in elems]
        if _query_result:
            return convert.convertQueryResult(items)
        else:
            return items
