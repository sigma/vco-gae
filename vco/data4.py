from uuid import uuid1 as _uuid
from workflows import getWorkflowImplementation

from google.appengine.api import memcache

import types
import models
import convert
import logging

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
            memcache.add(uri, elems)

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
