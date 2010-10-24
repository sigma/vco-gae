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
    def findAllResetCache(cls):
        uri = cls.findAllUri()
        memcache.delete(uri)

    @classmethod
    def findAll(cls, as_soap=False):
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

        if as_soap:
            elems = [e._asTarget() for e in elems]
        return elems

class _IdItem(_Item):

    @property
    def _id(self):
        return self._json.get('id', None)

    @classmethod
    def findByIdUri(cls, id):
        return "data4://id/%s/%s" % (cls.__name__, id)

    @classmethod
    def findByIdResetCache(cls, id):
        uri = cls.findByIdUri(id)
        memcache.delete(uri)

    @classmethod
    def findById(cls, id, as_soap=False):
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

        if as_soap:
            item = item._asTarget()
        return item

class Plugin(_Item):
    _model = models.Plugin
    _converter = convert.PluginConverter

    def __init__(self, model):
        _Item.__init__(self, model)

class Workflow(_IdItem):
    _model = models.Workflow
    _converter = convert.WorkflowConverter

    @classmethod
    def findByNameUri(cls, name):
        return "data4://id/%s/%s" % (cls.__name__, name)

    @classmethod
    def findByName(cls, name, as_soap=False):
        uri = cls.findByNameUri(name)
        elems = memcache.get(uri)
        if elems is None:
            query = cls._model.all()
            query.filter('name =', name)
            elems = [x for x in query]
            elems = [cls(i) for i in elems]
            memcache.add(uri, elems)

        if as_soap:
            elems = [e._asTarget() for e in elems]
        return elems

    def __init__(self, model):
        _IdItem.__init__(self, model)

    def run(self, inputs):
        wf = self._model.getById(self._id)
        tk_id = str(_uuid())
        token = models.WorkflowToken(id=tk_id,
                                     wf=wf)

        wf = getWorkflowImplementation(wf.wf_implem)
        token.put()
        wf.initTokens(token, inputs)
        return WorkflowToken(token)._asTarget()

class WorkflowToken(_IdItem):
    _model = models.WorkflowToken
    _converter = convert.WorkflowTokenConverter

    def __init__(self, model):
        _IdItem.__init__(self, model)

    def invalidate(self):
        self.findAllResetCache()
        self.findByIdResetCache(self._id)

    def cancel(self):
        self._model.getItem(self._id).cancel().put()
        self.invalidate()

    def answer(self, inputs):
        token = self._model.getItem(self._id)
        if token.state == models.WorkflowToken._WAITING:
            wf = token.wf

            wf = getWorkflowImplementation(wf.wf_implem)
            wf.updateTokens(token, inputs)
            self.invalidate()

    def result(self):
        return convert.convertWorkflowTokenResult(self._model.getItem(self._id))

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
