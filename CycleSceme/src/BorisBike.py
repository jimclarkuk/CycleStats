'''
Created on Aug 31, 2010

@author: jamesclark
'''
import urllib2
import MySQLdb
import simplejson

_urllib = urllib2

def run():
    req = urllib2.Request('http://api.bike-stats.co.uk/service/rest/bikestat/1')
    req.add_header('Accept', 'application/json')
    response = urllib2.urlopen(req)
    writeToDB(response)
    
    req = urllib2.Request('http://api.bike-stats.co.uk/service/rest/bikestat/2')
    req.add_header('Accept', 'application/json')
    response = urllib2.urlopen(req)
    writeToDB(response)

def writeToDB(query):
    result = simplejson.load(query)
    print result
    print result['dockStation']['@ID']

def setupDB():    
    # connect
    db = MySQLdb.connect(host="localhost", user="bike", passwd="bike", db="bike")
    # create a cursor
    cursor = db.cursor()
    
    cursor.execute ("""
       CREATE TABLE locations
       (
         id         INT(4),
         name       CHAR(100),
         latitude   CHAR(50),
         longitude  CHAR(50),
         installed  TINYINT(1),
         locked     TINYINT(1),
         temp       TINYINT(1)
       )
     """)
    cursor.execute ("""
       INSERT INTO locations VALUES
         ('1', 'River Street , Clerkenwell', '51.52916347', '-0.109970527', '0', '0', '0'),
         ('2', 'Phillimore Gardens, Kensington', '51.49960695', '-0.197574246', '0', '0', '0')
     """)
    print "Number of rows inserted: %d" % cursor.rowcount

    # execute SQL statement
    cursor.execute("SELECT * FROM locations")
    # get the resultset as a tuple
    result = cursor.fetchall()
    # iterate through resultset
    for record in result:
        print record[0] , "-->", record[1]

def setupDB_capacity():    
    # connect
    db = MySQLdb.connect(host="localhost", user="bike", passwd="bike", db="bike")
    # create a cursor
    cursor = db.cursor()
    
    cursor.execute ("""
       CREATE TABLE occupancy
       (
        id  BIGINT,
        location INT(4),
        readtime DATETIME,
        empty INT(4),
        inuse INT(4)
       )
       """)
            
if __name__ == '__main__':
    run()
    
