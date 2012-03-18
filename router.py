import os
import sys
import web
import site

''' Find out where we live '''
abspath = os.path.dirname(__file__)
site.addsitedir(abspath)

import controllers

urls = (
        '^/events/(.*)$', 'controllers.MeetupEvents',
        '^/rsvp/(.*)$', 'controllers.MeetupRsvp',
        '^/members/(.*)$', 'controllers.MeetupMembers',
       )



if __name__ == "__main__":
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()
else:
    app = web.application(urls, globals(), autoreload=False)
    application = app.wsgifunc()
