from google.appengine.ext import db

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

class WorkflowToken(db.Expando):
    id = db.StringProperty()
    title = db.StringProperty()
    wf = db.Key()

    cur_name = db.StringProperty()
    cur_state = db.StringProperty()
    global_state = db.StringProperty()

    start = db.StringProperty()
    end = db.StringProperty()

    xml = db.StringProperty()
