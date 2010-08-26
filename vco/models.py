from google.appengine.ext import db
from datetime import datetime

def clone_entity(e, **extra_args):
  """Clones an entity, adding or overriding constructor attributes.

  The cloned entity will have exactly the same property values as the original
  entity, except where overridden. By default it will have no parent entity or
  key name, unless supplied.

  Args:
    e: The entity to clone
    extra_args: Keyword arguments to override from the cloned entity and pass
      to the constructor.
  Returns:
    A cloned, possibly modified, copy of entity e.
  """
  klass = e.__class__
  props = dict((k, v.__get__(e, klass)) for k, v in klass.properties().iteritems())
  props.update(extra_args)
  return klass(**props)

class Plugin(db.Model):

    name = db.StringProperty()
    version = db.StringProperty()
    description = db.StringProperty()
    display = db.StringProperty()

class Parameter(db.Model):
    name = db.StringProperty()
    type = db.StringProperty()

class Workflow(db.Model):
    id = db.StringProperty()
    name = db.StringProperty()
    description = db.StringProperty()

    input = db.ListProperty(db.Key)
    output = db.ListProperty(db.Key)
    attributes = db.ListProperty(db.Key)

    wf_implem = db.StringProperty()

class TimedItem(db.Model):
    p_time_limit = db.DateTimeProperty(default=datetime.max)
    id = db.StringProperty()

    @classmethod
    def getCurrentItem(cls, id):
        now = datetime.now()
        query = cls.all()
        query.filter('id =', id)
        query.filter('p_time_limit >=', now)
        query.order('p_time_limit')
        return query.get()

    @classmethod
    def delFinalItems(cls, id):
        query = cls.all()
        query.filter('id =', id)
        query.filter('p_time_limit =', datetime.max)
        db.delete(query)

    @classmethod
    def delAllExpiredItems(cls):
        now = datetime.now()
        query = cls.all()
        query.filter('p_time_limit <', now)
        db.delete(query)

class WorkflowToken(TimedItem):
    title = db.StringProperty()
    wf = db.ReferenceProperty()

    cur_name = db.StringProperty()
    cur_state = db.StringProperty()
    state = db.StringProperty()

    start = db.DateTimeProperty()
    end = db.DateTimeProperty()

    xml = db.StringProperty()
