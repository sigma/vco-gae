from google.appengine.ext import db
from datetime import datetime
import logging

class Clonable(object):

    def clone(self, **args):
        klass = self.__class__
        props = dict((k, v.__get__(self, klass)) for k, v in klass.properties().iteritems())
        if isinstance(self, db.Expando):
            for k in self.dynamic_properties():
                props[k] = self.__getattr__(k)
        props.update(args)
        return klass(**props)

class BaseModel(db.Model, Clonable):
    pass

class BaseExpando(db.Expando, Clonable):
    p_props = db.StringListProperty()

    def setProperties(self, **props):
        self.clearProperties()
        l = []
        for k,v in props.items():
            pname = "prop_%s" % (k)
            self.__setattr__(pname, v)
            l.append(pname)
        self.p_props = l

    def clearProperties(self):
        for pname in self.p_props:
            self.__delattr__(pname)
        self.p_props = []

    def getProperties(self):
        res = {}
        for pname in self.p_props:
            val = getattr(self, pname)
            key = pname[5:]
            res[key] = val
        return res

class Plugin(BaseModel):

    name = db.StringProperty()
    version = db.StringProperty()
    description = db.StringProperty()
    display = db.StringProperty()

class Parameter(BaseModel):
    name = db.StringProperty(required=True)
    type = db.StringProperty(required=True)

class Workflow(BaseModel):
    id = db.StringProperty(required=True)
    name = db.StringProperty()
    description = db.StringProperty()

    input = db.ListProperty(db.Key)
    output = db.ListProperty(db.Key)
    attributes = db.ListProperty(db.Key)

    wf_implem = db.StringProperty(required=True)

    @classmethod
    def getById(cls, id):
        query = cls.all()
        query.filter('id =', id)
        return query.get()

class TimedItem(BaseExpando):
    p_time_upper_limit = db.DateTimeProperty(default=datetime.max)
    p_time_lower_limit = db.DateTimeProperty(default=datetime(1900, 1, 1))

    id = db.StringProperty(required=True)

    def setUpperLimit(self, date):
        self.p_time_upper_limit = date

    def setLowerLimit(self, date):
        self.p_time_lower_limit = date

    def invalidateAfter(self, date):
        self.setUpperLimit(date)

    def setFinal(self):
        self.setUpperLimit(datetime.max)

    def split(self, *dates):
        res = [self]
        current = self
        for d in dates:
            n = current.clone(p_time_lower_limit = d)
            current.p_time_upper_limit = d
            res.append(n)
            current = n
        return res

    def merge(self):
        query = self.__class__.all()
        query.filter('id =', self.id)
        query.filter('__key__ !=', self.key())
        db.delete(query)
        self.setFinal()
        return self

    def ttl(self):
        now = datetime.now()
        ttl = self.p_time_upper_limit - now
        return ttl.days * 86400 + ttl.seconds + 1

    @classmethod
    def allValid(cls, keys_only=False):
        now = datetime.now()
        query = cls.all(keys_only=keys_only)
        query.filter('p_time_upper_limit >=', now)
        query.order('p_time_upper_limit')
        return query

    @classmethod
    def allFinal(cls, keys_only=False):
        query = cls.all(keys_only=keys_only)
        query.filter('p_time_upper_limit =', datetime.max)
        return query

    @classmethod
    def allExpired(cls, keys_only=False):
        now = datetime.now()
        query = cls.all(keys_only=keys_only)
        query.filter('p_time_upper_limit <', now)
        return query

    @classmethod
    def getItem(cls, id):
        now = datetime.now()
        query = cls.allValid()
        query.filter('id =', id)
        return query.get()

class WorkflowToken(TimedItem):
    _COMPLETED = "completed"
    _CANCELLED = "canceled"
    _FAILED = "failed"
    _RUNNING = "running"
    _WAITING = "waiting"

    title = db.StringProperty()
    wf = db.ReferenceProperty(required=True)

    cur_name = db.StringProperty()
    cur_state = db.StringProperty()
    state = db.StringProperty(default=_RUNNING)

    start = db.DateTimeProperty(auto_now_add=True)
    end = db.DateTimeProperty()

    xml = db.StringProperty()

    def setResults(self, **res):
        self.clearResults()
        props = {}
        for out in self.wf.output:
            out = db.get(out)
            name = out.name
            props[name] = res.get(name)
        return self.setProperties(**props)

    def clearResults(self):
        return self.clearProperties()

    def getResults(self):
        return self.getProperties()

    def setRunning(self):
        self.state = self._RUNNING
        return self

    def setFailed(self):
        self.state = self._FAILED
        return self

    def setWaiting(self):
        self.state = self._WAITING
        return self

    def setCompleted(self):
        self.state = self._COMPLETED
        self.end = self.p_time_lower_limit
        self.setFinal()
        return self

    def complete(self):
        return self.setCompleted()

    def setCancelled(self):
        self.state = self._CANCELLED
        self.end = datetime.now()
        self.clearResults()
        self.setFinal()
        return self

    def cancel(self):
        if self.state == self._RUNNING:
            self.merge()
            return self.setCancelled()
        else:
            return self

class PluginObject(TimedItem):
    plugin = db.ReferenceProperty()
    type = db.StringProperty()
    obj_id = db.StringProperty()
