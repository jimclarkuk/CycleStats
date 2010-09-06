'''
Created on Aug 31, 2010

@author: jamesclark
'''
import urllib
import urllib2
import MySQLdb
import simplejson
from pygooglechart import Chart
from pygooglechart import SimpleLineChart
from pygooglechart import Axis


_urllib = urllib2
attrib = {'format': 'json'}
data = urllib.urlencode(attrib)
    
def run():
    req = urllib2.Request('http://api.bike-stats.co.uk/service/rest/bikestat/1?' + data)
    response = urllib2.urlopen(req)
    writeToDB(response)
    
    req = urllib2.Request('http://api.bike-stats.co.uk/service/rest/bikestat/2?' + data)
    response = urllib2.urlopen(req)
    writeToDB(response)

def writeToDB(query):
    result = simplejson.load(query)
    station = result['dockStation']
        # connect
    db = MySQLdb.connect(host="localhost", user="bike", passwd="bike", db="bike")
    # create a cursor
    cursor = db.cursor()
    print station
    statement = "INSERT INTO occupancy VALUES ('%s', '%s', '%s', '%s')" % (station['@ID'], result['updatedOn'], station['emptySlots'], station['bikesAvailable'])
    print statement
    cursor.execute(statement)
    print "Number of rows inserted: %d" % cursor.rowcount

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
    #cursor.execute ("DROP TABLE IF EXISTS occupancy")
    cursor.execute ("""
       CREATE TABLE occupancy
       (
        site INT(4),
        readtime CHAR(20),
        empty INT(4),
        available INT(4)
       )
       """)

def queryData():
    # connect
    db = MySQLdb.connect(host="localhost", user="bike", passwd="bike", db="bike")
    # create a cursor
    cursor = db.cursor()
    
    cursor.execute("""SELECT available, readtime FROM occupancy WHERE site='1'""")
    
    query = cursor.fetchall()
    
    # Set the vertical range from 0 to 100
    max_y = 20

    # Chart size of 200x125 pixels and specifying the range for the Y axis
    chart = SimpleLineChart(500, 300, y_range=[0, max_y])
    data = []
    y_axis = []
    for result in query:
        data.append(result[0])
        y_axis.append(result[1])
        
    chart.add_data(data)

    # Set the line colour to blue
    chart.set_colours(['0000FF'])

    # Set the vertical stripes
    chart.fill_linear_stripes(Chart.CHART, 0, 'CCCCCC', 0.2, 'FFFFFF', 0.2)

    # Set the horizontal dotted lines
#    chart.set_grid(0, 25, 5, 5)

    # The Y axis labels contains 0 to 100 skipping every 25, but remove the
    # first number because it's obvious and gets in the way of the first X
    # label.
    left_axis = range(0, max_y + 1, 2)
    left_axis[0] = ''
    chart.set_axis_labels(Axis.LEFT, left_axis)
    
    # X axis labels
    chart.set_axis_labels(Axis.BOTTOM, y_axis)
    
    print chart.get_url()

            
if __name__ == '__main__':
   # setupDB_capacity()
    queryData()
    
