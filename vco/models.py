from google.appengine.ext import db
from datetime import datetime
import logging

class Clonable(object):

    def clone(self, **args):
        klass = self.__class__
        props = dict((k, v.__get__(self, klass)) for k, v in klass.properties().iteritems())
        props.update(args)
        return klass(**props)

class BaseModel(db.Model, Clonable):
    pass

class BaseExpando(db.Expando, Clonable):
    pass

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

class TimedItem(BaseExpando):
    p_time_limit = db.DateTimeProperty(default=datetime.max)
    id = db.StringProperty(required=True)

    def invalidateAfter(self, date):
        self.p_time_limit = date

    def setFinal(self):
        self.p_time_limit = datetime.max

    @classmethod
    def allValid(cls):
        now = datetime.now()
        query = cls.all()
        query.filter('p_time_limit >=', now)
        query.order('p_time_limit')
        return query

    @classmethod
    def getItem(cls, id):
        now = datetime.now()
        query = cls.allValid()
        query.filter('id =', id)
        return query.get()

    @classmethod
    def delFutureItems(cls, id):
        query = cls.all()
        query.filter('id =', id)
        query.filter('p_time_limit =', datetime.max)
        db.delete(query)

    @classmethod
    def allExpired(cls):
        now = datetime.now()
        query = cls.all()
        query.filter('p_time_limit <', now)
        return query

class WorkflowToken(TimedItem):
    title = db.StringProperty()
    wf = db.ReferenceProperty(required=True)

    cur_name = db.StringProperty()
    cur_state = db.StringProperty()
    state = db.StringProperty(default="running")

    start = db.DateTimeProperty(auto_now_add=True)
    end = db.DateTimeProperty()

    xml = db.StringProperty()

    p_results = db.StringListProperty()

    def setResults(self, res):
        self.clearResults()
        l = []
        for out in self.wf.output:
            out = db.get(out)
            name = out.name
            pname = "res_%s" % (name)
            self.__setattr__(pname, res.get(name))
            l.append(pname)
        self.p_results = l

    def clearResults(self):
        for pname in self.p_results:
            self.__delattr__(pname)
        self.p_results = []

    def getResults(self):
        res = {}
        for pname in self.p_results:
            val = getattr(self, pname)
            key = pname[4:]
            res[key] = val
        return res

    def complete(self):
        self.state = "completed"
        self.setFinal()

    def cancel(self):
        self.state = "canceled"
        self.end = datetime.now()
        self.clearResults()
        self.setFinal()
