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

    @classmethod
    def findAll(cls):
        uri = "data4://all/%s" % (cls.__name__)
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
            memcache.add(uri, elems, ttl)

        items = [cls(i) for i in elems]
        return items

class _IdItem(_Item):

    @classmethod
    def findById(cls, id):
        uri = "data4://id/%s/%s" % (cls.__name__, id)
        item = memcache.get(uri)

        if item is None:
            if issubclass(cls._model, models.TimedItem):
                item = cls._model.getItem(id)
                ttl = item.ttl()
                memcache.add(uri, item, ttl)
            else:
                query = cls._model.all()
                query.filter('id =', id)
                item = query.get()
                memcache.add(uri, item)

        if item is not None:
            item = cls(item)
        return item

class Plugin(types.ModuleInfo, _Item):
    _model = models.Plugin

    def __init__(self, model):
        types.ModuleInfo.__init__(self)
        self.__model = model

        convert.convertPlugin(model, target=self)

class Workflow(types.Workflow, _IdItem):
    _model = models.Workflow

    @classmethod
    def findByName(cls, name):
        uri = "data4://id/%s/%s" % (cls.__name__, id)
        elems = memcache.get(uri)
        if elems is None:
            query = cls._model.all()
            query.filter('name =', name)
            elems = [x for x in query]
            memcache.add(uri, elems)

        items = [cls(i) for i in elems]
        return items

    def __init__(self, model):
        types.Workflow.__init__(self)
        self.__model = model

        convert.convertWorkflow(model, target=self)

    def run(self, inputs):
        wf = self.__model
        tk_id = str(_uuid())
        token = models.WorkflowToken(id=tk_id,
                                     wf=wf)

        wf = getWorkflowImplementation(wf.wf_implem)
        token.put()
        wf.initTokens(token, inputs)
        return WorkflowToken(token)

class WorkflowToken(types.WorkflowToken, _IdItem):
    _model = models.WorkflowToken

    def __init__(self, model):
        types.WorkflowToken.__init__(self)
        self.__model = model

        convert.convertWorkflowToken(model, target=self)

    def cancel(self):
        self.__model.cancel().put()

    def answer(self, inputs):
        token = self.__model
        if token.state == models.WorkflowToken._WAITING:
            wf = token.wf

            wf = getWorkflowImplementation(wf.wf_implem)
            wf.updateTokens(token, inputs)

    def result(self):
        return convert.convertWorkflowTokenResult(self.__model)

class FinderResult(types.FinderResult, _IdItem):
    _model = models.PluginObject

    def __init__(self, model):
        types.FinderResult.__init__(self)
        self.__model = model

        convert.convertPluginObject(model, target=self)

    @classmethod
    def find(cls, type, id=None, query=None, _query_result=False):
        uri = "data4://finder/%s/%s/%s" % (type, id, query)
        plugin, type = type.split(':')
        plugin = models.Plugin.all().filter('name =', plugin).get()
        elems = memcache.get(uri)
        if elems is None:
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
            memcache.add(uri, elems, ttl)

        items = [cls(i) for i in elems]
        if _query_result:
            return convert.convertQueryResult(items)
        else:
            return items
