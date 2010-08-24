from google.appengine.ext import db
from google.appengine.api.datastore_errors import BadQueryError

class Plugin(db.Model):

    name = db.StringProperty()
    version = db.StringProperty()
    description = db.StringProperty()
    display = db.StringProperty()
