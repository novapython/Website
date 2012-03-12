import sys
import requests
import json
import hashlib
import redis


class MeetupAPI(object):
    '''
        Quick class to issue GET requests to the Meetup API
    '''

    def __init__(self, key,
                 url='http://api.meetup.com/2/',
                 headers={'content-type': 'application/json'}):
        self.key = key
        self.url = url
        self.headers = headers
        self.cache = redis.Redis(host='localhost')

    def __getattr__(self, name):

        def method(*opts):
            return self.call(name, opts[0])
        return method

    def call(self, method, params):
        paramlist = ['key=%s' % self.key]
        for k, v in params.iteritems():
            paramlist.append('%s=%s' % (k, v))

        meetup_request = '%s/%s?%s' % (self.url, method, '&'.join(paramlist))
        hash = hashlib.sha224(meetup_request).hexdigest()
        meetup_response = self.cache.get(hash)
        if meetup_response is None:
            r = requests.get(meetup_request, headers=self.headers)
            meetup_response = json.dumps({'status': r.status_code,
                                          'text': r.text})
            self.cache.set(hash, meetup_response)
            self.cache.expire(hash, 86400)
        return json.loads(meetup_response)

if __name__ == "__main__":
    key = 'MeetupAPI Key'
    meetup = MeetupAPI(key)
    request = meetup.events({'group_id': '1546792', 'page': 20})
    print request
