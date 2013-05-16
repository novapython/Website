import logging


logging.basicConfig(level=logging.DEBUG,
                    filename='/tmp/novapy.log',
                    filemode='w')
rlog = logging.StreamHandler()
rlog.setLevel(logging.WARNING)
logging.getLogger('').addHandler(rlog)

logger = logging.getLogger('novapy')
apikey = '7d4d5e7d372b181a1d273b767f413742'