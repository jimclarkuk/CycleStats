'''
Created on Aug 31, 2010

@author: jamesclark
'''
import urllib2

_urllib = urllib2

def run():
    print "foo"
    req = urllib2.Request('http://api.bike-stats.co.uk/service/rest/bikestat/1')
    response = urllib2.urlopen(req)
    print response.read()

if __name__ == '__main__':
    run()
    
