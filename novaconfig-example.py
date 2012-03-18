import web
import logging


logging.basicConfig(level=logging.DEBUG,
                    filename='/tmp/novapy.log',
                    filemode='w')
rlog = logging.StreamHandler()
rlog.setLevel(logging.WARNING)
logging.getLogger('').addHandler(rlog)

logger = logging.getLogger('novapy')
apikey = 'MyAPIKey'
