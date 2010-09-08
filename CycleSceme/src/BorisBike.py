'''
Created on Aug 31, 2010

@author: jamesclark
'''
import urllib
import urllib2
import MySQLdb
import simplejson
import time
import getopt, sys
from pygooglechart import Chart
from pygooglechart import SimpleLineChart
from pygooglechart import Axis


_urllib = urllib2
attrib = {'format': 'json'}
data = urllib.urlencode(attrib)
db = MySQLdb.connect(host="localhost", user="bike", passwd="bike", db="bike")
logging = 0
            
def usage():
    print "usage: ", sys.argv[0], " [-l location ID] | [-a] | [-m]"
    print "-l [location ID] : Get the graph for a given location"
    print "-a : Get the graphs for all locations"
    print "-m : Queries the bike stats every 5mins for eeeever"
    sys.exit(2)

def log(message):
    if logging:
        print message
            
def record_for(ID):
    req = urllib2.Request(('http://api.bike-stats.co.uk/service/rest/bikestat/%s?' % ID) + data)
    response = urllib2.urlopen(req)
    writeToDB(response)

def writeToDB(result):
    if 'dockStation' not in result:
        print 'Error bitches!'
        print result
        return
    statement = "INSERT INTO occupancy VALUES "
    for station in result['dockStation']:
        # create a cursor
        log(station)
        statement += """('%s', '%s', '%s', '%s'), """ % (station['@ID'], result['updatedOn'], station['emptySlots'], station['bikesAvailable'])
    log(statement)
    cursor = db.cursor()
    cursor.execute(statement.rstrip(', '))
    log("Number of rows inserted: %d" % cursor.rowcount)

def setup_db():    
    # create a cursor
    cursor = db.cursor()
    cursor.execute ("DROP TABLE IF EXISTS locations")
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
    
    insert = """INSERT INTO locations VALUES"""
#         ('1', 'River Street , Clerkenwell', '51.52916347', '-0.109970527', '0', '0', '0'),
    locations = get_all_locations()
    for location in locations['dockStation']:
        insert += """('%s', '%s', '%s', '%s', '%s', '%s', '%s'), """ % (location['@ID'], location['name'].replace("'", "\\'"), location['latitude'], location['longitude'], 0, 0, 0)#location['installed'],location['locked'],location['temporary']
    insert = insert.rstrip(', ')
    
    cursor.execute(insert)

def setupDB_capacity():    
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

def queryData(ID=1):
    # connect
    
    # create a cursor
    cursor = db.cursor()
    
    #cursor.execute("SELECT available, readtime FROM occupancy WHERE site='%s'" % ID)
    cursor.execute("SELECT available, readtime FROM occupancy WHERE site='%s'" % ID)
    query = cursor.fetchall()
    log(query)
    # Set the vertical range from 0 to 100
    max_y = 50

    # Chart size of 200x125 pixels and specifying the range for the Y axis
    chart = SimpleLineChart(500, 300, y_range=[0, max_y])
    data, y_axis = ([[x[i] for x in query] for i in [0, 1]])    
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
    
    return chart

def get_ids():
    # create a cursor
    cursor = db.cursor()
    
    #cursor.execute("SELECT available, readtime FROM occupancy WHERE site='%s'" % ID)
    cursor.execute("SELECT id FROM locations")
    return cursor.fetchall()
 
def get_all_locations():
    req = urllib2.Request('http://api.bike-stats.co.uk/service/rest/bikestats?' + data)
    response = urllib2.urlopen(req)
    return simplejson.load(response)  
   
def print_all_graphs():
    for id in get_ids():
        print queryData(id[0]).get_url()

def monitor():
    print "started"
    while 1:
        print "running"
        writeToDB(get_all_locations())
        print "done for now"
        time.sleep(300)
    print "done"

def main():
    try:
        #u:st: [there is a parameter following -u and -t options,option -s without parameter]
        opts, args = getopt.getopt(sys.argv[1:], "al:m")
        mon = 0
        get_location = 0
        get_all = 0
    except getopt.GetoptError:
        #print help information and exit:
        sys.stdout = sys.stderr
        usage()
    for o, a in opts:
        if o == "-a":
            get_all = 1
        if o == "-m":
            mon = 1
        if o == "-l":
            get_location = 1
            id = a
    if get_all and get_location:
        print "Ooops, do you want all locations (-a) or a single location (-l [ID])"
        usage()
    if mon:
        monitor()
        return
    if get_all:
        print_all_graphs()
        return
    if get_location:
        print queryData(id).get_url()
        return
    usage()
            
if __name__ == '__main__':
    main()
