import os
import web
import site
import logging

""" Find out where we live """
abspath = os.path.dirname(__file__)
site.addsitedir(abspath)

from templates import render_template
import controllers

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

urls = (
        '^/events/(.*)$', 'controllers.MeetupEvents',
        '^/rsvp/(.*)$', 'controllers.MeetupRsvp',
        '^/members/(.*)$', 'controllers.MeetupMembers',
        '/', 'Home',
       )


class Home(object):
    def GET(self):
        logger.debug('Rendering index')
        web.header('Content-Type', 'text/html')
        return render_template('index.html')

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()
else:
    app = web.application(urls, globals(), autoreload=False)
    application = app.wsgifunc()
