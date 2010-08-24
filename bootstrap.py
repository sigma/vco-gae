# Run this in admin console to populate the datastore

from vco.models import Plugin

p = Plugin(name="dummy", version="0.1",
           description="Dummy plug-in", display="Dummy")
p.put()
