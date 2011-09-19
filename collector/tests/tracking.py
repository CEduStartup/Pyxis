from gevent import monkey
monkey.patch_socket()

import sys, os
sys.path.insert(0, '%s/..' % os.getcwd())
sys.path.insert(1, '%s/' % os.getcwd())

from Tracker import Tracker
from trackers import XmlResourceTracker
from config import logger
import gevent
import urllib2

class DummyStorage:
    def put(self, tracker, data):
        logger.info('put - tracker: %s (%s), data: %s' % (tracker.get_id(), tracker.get_source(), data))

def run_trackers():
    logger.info('main')
    storage = DummyStorage()

    greenlets = []
    for idx, url in enumerate(['http://informer.gismeteo.ru/xml/33393_1.xml',
                               'http://informer.gismeteo.ru/xml/33345_1.xml',
                               'http://informer.gismeteo.ru/xml/33526_1.xml',
                               'http://informer.gismeteo.ru/xml/33651_1.xml',
                               'http://informer.gismeteo.ru/xml/88346_1.xml',
                               'http://informer.gismeteo.ru/xml/99870_1.xml']):
        tracker = XmlResourceTracker('tracker_%d' % idx, storage)
        tracker.set_source(url)
        greenlets.append(gevent.spawn(tracker.grab_data))
    logger.info('doing')
    gevent.joinall(greenlets)

def run_urllib2():
	logger.info('running urllib2')
	request = urllib2.Request('http://habrahabr.ru')
	#request = urllib2.Request('http://habrahabr.ru/search/?q=python')
	response = urllib2.urlopen(request)
	logger.info('read %d bytes' % len(response.read()))

def run_grab_data():
    logger.info('running grabdata')
    url = 'http://habrahabr.ru/search/?q=python'
    storage = DummyStorage()
    tracker = Tracker('tracker_x', storage)
    tracker.set_source(url)
    tracker.grab_data()

def test_logger():
    pass

if __name__ == '__main__':
    run_trackers()
    #run_urllib2()
    #run_grab_data()
    #test_logger()
