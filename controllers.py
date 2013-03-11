import web
import logging
import json
import time
from Meetup import MeetupAPI
from novaconfig import apikey, logger


class MeetupMembers(object):
    '''
        Returns a list of all members in your meetup

        Members come and go fairly regularly, so this list
        is updated every hour.
    '''

    def GET(self, cmd):
        logger.debug('GET /meetup/members/%s' % cmd)
        decoder = json.JSONDecoder()
        meetup = MeetupAPI(apikey, lifetime=3600)
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
                raise web.HTTPError("%d %s" % (request['status'], text['details']), {}, f)
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

        Generally Meetups aren't added very often, so we
        refresh our list once a day.
    '''

    def GET(self, cmd):
        logger.debug('GET /meetup/events/%s' % cmd)
        meetup = MeetupAPI(apikey, lifetime=3600)
        request = meetup.events({'group_id': cmd, 'page': 20})

        try:
            if request['status'] != 200:
                text = json.JSONDecoder().decode(request['text'])
                # Meetup gives us detailed error conditions in most cases
                # but I've had these fields not present before
                if 'problem' not in text:
                    text['problem'] = 'Not specified'
                if 'details' not in text:
                    text['details'] = 'Not specified'
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
        decoder = json.JSONDecoder()
        '''
            The first call get a list of all our past meetups. This
            list expand as meetups complete, so we should refresh it
            once a day
        '''
        meetup = MeetupAPI(apikey, lifetime=86400)

        '''
            The second meetup instance uses a deprecated API to list
            the 'attended' counts. This is only available on completed
            meetups, and is requested per meetup. So it never changes,
            and we can permanently cache the response.
        '''
        m1 = MeetupAPI(apikey, 'http://api.meetup.com/', lifetime=0)
        finished = False
        results = []
        offset = 0

        while finished is False:
            eventlist = meetup.events({'status': 'past',
                                   'group_id': cmd,
                                   'offset': offset,
                                   'page': 20})

            try:
                results.append(decoder.decode(eventlist['text'])['results'])
                meta = decoder.decode(eventlist['text'])['meta']
                count += meta['count']
                if count == meta['total_count']:
                    finished = True
                else:
                    offset += 1
            except Exception, e:
                logger.debug(eventlist)
                text = decoder.decode(eventlist['text'])
                # Meetup gives us detailed error conditions in most cases
                # but I've had these fields not present before
                if 'problem' not in text:
                    text['problem'] = 'Not specified'
                if 'details' not in text:
                    text['details'] = 'Not specified'
                raise web.HTTPError("%d %s" % (eventlist['status'], text['problem']), {}, text['details'])

        for event in results:
            name = None
            count = None
            attendee = None
            eventdate = None
            try:
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
