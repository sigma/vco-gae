from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from vco.models import WorkflowToken
import logging
from datetime import datetime, timedelta

class TimedItemConsolidate(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        consolidated_classes = [WorkflowToken,]

        for cls in consolidated_classes:
            query = cls.allExpired()
            nb = query.count()
            self.response.out.write("Consolidated %d items of class '%s'" % (nb, cls))
            db.delete(query)

class WorkflowTokenPurge(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        limit = datetime.now() + timedelta(hours=-2)

        query = WorkflowToken.allFinal()
        query.filter('end <', limit)
        nb = query.count()
        self.response.out.write("Purged %d workflow tokens" % (nb))
        db.delete(query)

application = webapp.WSGIApplication(
                                     [('/tasks/consolidate', TimedItemConsolidate),
                                      ('/tasks/purge', WorkflowTokenPurge)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
