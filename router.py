import os
import web
import site
from templates import render_template

''' Find out where we live '''
abspath = os.path.dirname(__file__)
site.addsitedir(abspath)

import controllers

urls = (
        '^/events/(.*)$', 'controllers.MeetupEvents',
        '^/rsvp/(.*)$', 'controllers.MeetupRsvp',
        '^/members/(.*)$', 'controllers.MeetupMembers',
        '/', 'Home',
       )


class Home(object):
    def GET(self):
        render_template('index.html')

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()
else:
    app = web.application(urls, globals(), autoreload=False)
    application = app.wsgifunc()
