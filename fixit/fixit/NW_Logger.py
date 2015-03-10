import logging
import logging.handlers
host='192.168.100.79:80'
url='/logbook/fixit/push/'

def get_logger_obj():
    nwlogger = logging.getLogger('test_fixit')
    nwlogger.setLevel(logging.DEBUG)
    sysh=logging.handlers.HTTPHandler(host, url, method='GET')
    formatter = logging.Formatter('%(asctime)s : %(name)s:'\
        ' [%(process)d] :'\
        ' %(module)s :'\
        ' %(pathname)s :'\
        ' %(lineno)d :'\
        ' %(funcName)s :'\
        ' %(levelname)s : %(message)s')
    sysh.setFormatter(formatter)
    nwlogger.addHandler(sysh)
    return nwlogger

