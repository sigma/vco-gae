from google.appengine.ext import db
from google.appengine.api.datastore_errors import BadQueryError

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
