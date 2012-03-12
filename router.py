import site
site.addsitedir('/var/www/novapython/')
site.addsitedir('/var/www/novapython/lib/python2.6/site-packages')

import logging
import web
import sys
import json
import time
from Meetup import MeetupAPI

urls = (
        '^/events/(.*)$', 'MeetupEvents',
        '^/rsvp/(.*)$', 'MeetupRsvp',
        '^/members/(.*)$', 'MeetupMembers'
       )

logging.basicConfig(level=logging.DEBUG,
                    filename='/tmp/novapy.log',
                    filemode='w')
rlog = logging.StreamHandler()
rlog.setLevel(logging.WARNING)
logging.getLogger('').addHandler(rlog)
logger = logging.getLogger('novapy')

''' Set your Meetup API Key '''
meetupkey = 'YourKey'


class MeetupMembers(object):
    '''
        Returns a list of all members in your meetup
    '''

    def GET(self, cmd):
        logging.debug('GET /meetup/events/%s' % cmd)
        decoder = json.JSONDecoder()
        meetup = MeetupAPI(meetupkey)
        request = meetup.members({'group_id': cmd, 'page': 20})
        response = decoder.decode(request['text'])['results']
        meta = decoder.decode(request['text'])['meta']
        offset = 1
        logging.debug(int(meta['total_count'] / 20.0))
        for x in range(0, int(meta['total_count'] / 20.0)):
            logging.debug('offset %d' % offset)
            item = meetup.members({'group_id': cmd, 'page': 20, 'offset': offset})
            response.extend(decoder.decode(item['text'])['results'])
            offset += 1

        logging.debug(response)
        return json.dumps(response)

       
class MeetupEvents(object):
    '''
        Returns a list of all future meetup events
    '''

    def GET(self, cmd):
        logging.debug('GET /meetup/events/%s' % cmd)
        try:
            meetup = MeetupAPI(meetupkey)
            request = meetup.events({'group_id': cmd, 'page': 20})
        except Exception, e:
            return "%s" % e
        return request['text']


class MeetupRsvp(object):
    '''
        Aggregates API data for past meetup events from two
        versions of the MeetupAPI.

        Returns a list objects
            {
                'rsvp': The RSVP count,
                'attended': The number who attended(defaults to rsvp!),
                'name': The name of the meetup,
                'date': The date the meetup took place
            }
    '''

    def GET(self, cmd):
        logging.debug('GET /meetup/rsvp/%s' % cmd)
        try:
            meetup = MeetupAPI(meetupkey)
            m1 = MeetupAPI(meetupkey, 'http://api.meetup.com/')
        except Exception, e:
            print e
        logging.debug('1')
        eventlist = meetup.events({'status': 'past',
                                   'group_id': cmd,
                                   'page': 20})['text']
        result = []
        logging.debug('2')
        for event in json.JSONDecoder().decode(eventlist)['results']:
            name = None
            count = None
            attendee = None
            eventdate = None
            try:
                logging.debug('3')
                name = event['name']
                count = int(event['yes_rsvp_count'])
                if count is None:
                    count = 0

                # event['time'] is UTC milliseconds since epoch
                starttime = time.localtime(event['time'] / 1000)
                eventdate = time.strftime('%Y-%m-%d %H:%M:%S', starttime)

                ev = json.JSONDecoder().decode(
                        m1.events({'id': event['id']})['text'])
                if len(ev['results']) > 0:
                    attendee = int(ev['results'][0]['attendee_count'])
                    if attendee is None:
                        attendee = 0
            except KeyError, e:
                logging.warning('%s' % e)
                pass
            except Exception, e:
                logging.warning('%s' % e)
                pass

            result.append({'rsvp': count,
                           'attended': attendee,
                           'name': name,
                           'date': eventdate})

        return json.dumps(result)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()
else:
    app = web.application(urls, globals(), autoreload=False)
    application = app.wsgifunc()
