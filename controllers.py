import web
import logging
import json
import time
from Meetup import MeetupAPI
from novaconfig import apikey, logger


class MeetupMembers(object):
    '''
        Returns a list of all members in your meetup
    '''

    def GET(self, cmd):
        logger.debug('GET /meetup/events/%s' % cmd)
        decoder = json.JSONDecoder()
        meetup = MeetupAPI(apikey)
        response = None
        meta = None

        request = meetup.members({'group_id': cmd, 'page': 20})
        try:
            response = decoder.decode(request['text'])['results']
            meta = decoder.decode(request['text'])['meta']
        except Exception, e:
            logger.debug(request)
            if 'text' in request:
                text = json.JSONDecoder().decode(request['text'])
                raise web.HTTPError("%d %s" % (request['status'], text['problem']), {}, f)
            raise web.InternalError(e)
        offset = 1
        logger.debug(int(meta['total_count'] / 20.0))
        for x in range(0, int(meta['total_count'] / 20.0)):
            logger.debug('offset %d' % offset)
            item = meetup.members({'group_id': cmd, 'page': 20, 'offset': offset})
            response.extend(decoder.decode(item['text'])['results'])
            offset += 1

        logger.debug(response)
        return json.dumps(response)


class MeetupEvents(object):
    '''
        Returns a list of all future meetup events
    '''

    def GET(self, cmd):
        logger.debug('GET /meetup/events/%s' % cmd)
        meetup = MeetupAPI(apikey)
        request = meetup.events({'group_id': cmd, 'page': 20})

        try:
            if request['status'] != 200:
                text = json.JSONDecoder().decode(request['text'])
                raise web.HTTPError("%d %s" % (request['status'], text['problem']), {}, text['details'])
        except KeyError, e:
            logger.warning('events failed')
            raise web.InternalError('Bad Object')
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
        logger.debug('GET /meetup/rsvp/%s' % cmd)
        meetup = MeetupAPI(apikey)
        m1 = MeetupAPI(apikey, 'http://api.meetup.com/')
        eventlist = meetup.events({'status': 'past',
                                   'group_id': cmd,
                                   'page': 20})
        result = []
        try:
            results = json.JSONDecoder().decode(eventlist['text'])['results']
        except Exception, e:
            logger.debug(eventlist)
            text = json.JSONDecoder().decode(eventlist['text'])
            raise web.HTTPError("%d %s" % (eventlist['status'], text['problem']), {}, text['details'])
        for event in results:
            name = None
            count = None
            attendee = None
            eventdate = None
            try:
                logger.debug('3')
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
                logger.warning('%s' % e)
                pass
            except Exception, e:
                logger.warning('%s' % e)
                pass

            result.append({'rsvp': count,
                           'attended': attendee,
                           'name': name,
                           'date': eventdate})

        return json.dumps(result)
