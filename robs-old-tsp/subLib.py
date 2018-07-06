from __future__ import print_function
from peewee import *
import sys, os, pickle
from datetime import date, datetime, timedelta, time
from optimizers import shortestPath, solve_tsp

directory = '/home/robj/Scripts/subway-record/robs-old-tsp/'
routes = directory+'gtfs/routes.txt'
stops = directory+'gtfs/stops.txt'
trips = directory+'gtfs/trips.txt'
stop_times = directory+'gtfs/stop_times.txt'
transfers = directory+'gtfs/transfers.txt'
calendar = directory+'gtfs/calendar.txt'
calendar_dates = directory+'gtfs/calendar_dates.txt'
shapes = directory+'gtfs/shapes.txt'
dbname = directory+'subway.db'
graphname = directory+'graph.p'
shortest_pathsname = directory+'shortest_paths.p'
extra_transfers = directory+'extra_transfers.txt'


#################################################
## For use in files that import sublib, 
##  Here's a handy function for checking
##  if the stop-time database has already
##  been generated on your computer!
#################################################
def checkForDB(dbname):
  return os.path.isfile(dbname)

def checkForPickle(picklename):
  return os.path.isfile(picklename)

db = SqliteDatabase(dbname)
###############################################
## Object Declarations!
###############################################
class Route(Model):
  name = CharField()
  route_id = CharField(unique=True)
  class Meta:
    database = db

class Stop(Model):
  name = CharField()
  stop_id = CharField(unique=True)
  class Meta:
    database = db
  # This should get the adjacent stops to this one
  # it's a little sloppy but gets the job done
  # if xferPenalty is -1, transfers are not considered
  # if it's >0 it's xferPenalty seconds
  def adjacent(self, xfer=-1):
    outputList = []
    adj = {}
    #pull out all stoptimes at this stop
    stoptimes = StopTime.select().where(
        StopTime.stop==self)
    for s in stoptimes:
      #From those stoptimes pull out all before
      # or after in sequence from this one
      adjacentStopTimes = StopTime.select().where(
          (StopTime.trip==s.trip) & (
          (StopTime.seq==s.seq-1) | (
          StopTime.seq==s.seq+1)))
      for a in adjacentStopTimes:
        #from those, pull out the distance/time
        dist = timeAbslouteValue(a.time, s.time)
        #then keep track of the running total
        if a.stop.stop_id not in adj:
          adj[a.stop.stop_id] = (dist,1)
        else:
          total,n = adj[a.stop.stop_id]
          adj[a.stop.stop_id] = (total+dist, n+1)
    #once we've got the total for all adj stops
    # take the average for each adjacent stop
    for a in adj:
      total,n = adj[a]
      outputList.append((a,total/n))
    #Adjacent stops via transfers
    if xfer>=0:
      trans = Transfer.select().where(
          Transfer.frm == self)
      for t in trans:
        transTime = timeAbslouteValue(
            time.min, t.time)
        addPenalty = transTime + timedelta(
            seconds=xfer)
        outputList.append((t.to.stop_id,addPenalty))
    return outputList

class Trip(Model):
  route = ForeignKeyField(Route,
      related_name='routes')
  direction = BooleanField()
  name = CharField()
  schedule = CharField()
  trip_id = CharField(unique=True)
  class Meta:
    database = db

class StopTime(Model):
  time = TimeField()
  seq = IntegerField()
  stop = ForeignKeyField(Stop,
      related_name='stops')
  trip = ForeignKeyField(Trip,
      related_name='trips')
  class Meta:
    database = db

class Transfer(Model):
  time = TimeField()
  to = ForeignKeyField(Stop,
      related_name='to stops')
  frm = ForeignKeyField(Stop,
      related_name='from stops')
  class Meta:
    database = db

def lineToCSV(line):
  insidequote = False
  sanitizedString = ''
  for ch in line:
    if insidequote:
      if ch == ',':
        pass
      elif ch == '"':
        insidequote = False
      else:
        sanitizedString += ch
    else:
      if ch == '"':
        insidequote = True
      elif ch == '\n' or ch == '\r':
        pass
      else:
        sanitizedString += ch
  return sanitizedString.split(',')
def CSVToDict(line,keys):
  if len(line) != len(keys): 
    raise ValueError(
        'length of line and keys are not equal')
  d = {}
  for i in range(len(keys)):
    d[keys[i]] = line[i]
  return d

def getDictList(filename):
  with open(filename) as r:
    k = lineToCSV(r.readline())
    #print(k)
    #print(r.readline())
    #print(r.readline())
    #print(lineToCSV(r.readline()))
    d = []
    for l in r:
      d.append(CSVToDict(lineToCSV(l),k))
    return d

def printDictList(dl):
  for d in dl:
    for k in d:
      print(k + '-')
      print('\t'+d[k])
    print('--------------------')

# function for dealing with the strange way
# they do times above 23:59
def convertTime(t):
  h = int(t[:2])
  if h>23: h=h-24
  return str(h).zfill(2) + t[2:]

#converts between transfer time (seconds)
#so we can easily add it to trip times etc
def secondsToHMS(s):
  hours = int(s)/3600
  leftover = int(s) - hours*3600
  mins  = leftover/60
  leftover = leftover - mins*60
  secs = leftover
  return '{0}:{1}:{2}'.format(
      str(hours).zfill(2), str(mins).zfill(2),
      str(secs).zfill(2))

#subtracting times is a lil tricky becuase
# it's a cyclical schedule, return type should
# be a datetime.timedelta object
#Because of cyclical stuff, only deal with times
# less than an hour apart
# for now this is the absloute value
def timeAbslouteValue(timeA, timeB):
  a = datetime.combine(
      date.min, timeA) - datetime.min
  b = datetime.combine(
      date.min, timeB) - datetime.min
  if timeA.hour == 23 and timeB.hour < 2:
    b += timedelta(days=1) #b is tomorr
  elif timeB.hour == 23 and timeA.hour <2:
    a += timedelta(days=1) #a is tomorr
  return abs(a-b)

#give me a list of all the stops (useful for
# iterating through stuff
# IMPORTANT: all this does is get rid of 
#  SIR stops
def nyctStops():
  #SIR stops are S09 and above
  #S0-4 are shuttle stops btw
  def sir(stp):
    return stp.stop_id[0] == 'S' and (
        int(stp.stop_id[1:])>=9)
  stops = Stop.select()
  nyct = []
  for s in stops:
    if not sir(s) and s.stop_id!='H19':
      nyct.append(s)
  return nyct
    
def listLineStops(route,variant=0):
  rte = Route.get(Route.route_id==route)
  variantsList = []
  variantsDict = {} #{trip rollsign: trip object}
  trips = Trip.select().where(Trip.route==rte)
  for t in trips:
    if t.name not in variantsDict:
      variantsList.append(t.name)
      variantsDict[t.name]=t
  print('The {0} has {1} variants:'.format(
      rte.route_id,len(variantsList)))
  for i,v in enumerate(variantsList):
    print('  {0} -To: {1}'.format(
        i,variantsDict[variantsList[i]].name))
  print('Displaying Variant {0}'.format(variant))
  trp = variantsDict[variantsList[variant]]
  stops = StopTime.select().where(
      (StopTime.trip==trp)).order_by(StopTime.seq)
  for stp in stops:
    print('{0} - {1}'.format(
        stp.stop.stop_id,stp.stop.name))

#################################################
## Route List:
#route_list = getDictList(routes)
## Field Descriptions:
##   route_long_name: Long name describing route, 
##       Typically what's on the subway car roll 
##       sign, Example: '7 Avenue Express'
##   route_type: Not entirely clear, all non-
##       Staten Island routes are '1' SI is '2'
##   route_text_color: Typically left blank
##   route_color: Hex value of route bullet color
##       Example: '00933C' for 456
##   agency_id: agency, example: 'MTA NYCT'
##   route_id: Internal short name. for most 
##       routes this is identical to the short
##       name, but not for all 
##       S->FS, S->H, S->GS, SIR-> SI
##   route_url: website with schedule info
##   route_desc: long description of service
##   route_short_name: name on bullets (A,B,C..)
#################################################
## Stop List:
#stop_list  = getDictList(stops)
## Field Descriptions:
##   stop_lat: Stop lattitude, general
##   stop_code: Unclear, but always ''
##   stop_lon: Stop Longitude, general
##   parent_station: Stations are split into 3 
##       stations, N, S, and _ 
##       Example: St George: S31, S31N, S31S
##       in "parent" stations, this field is ''
##       In "child" stations this is the parent
##   stop_url: Who knows, not important, 
##       usually left blank
##   stop_id: string to identify station, in
##       'child' stations this begins witn NorS
##   stop_desc: unclear if this is ever used
##   stop_name: String name Ex: 'Tompkinsville'
##   location_type: parent-1, child-0
##   zone_id: Always blank
#################################################
## Trip List:
#trip_list  = getDictList(trips)
## Field Descriptions:
##   block_id: Always Blank
##   route_id: Same field as
##       route_list['route_id']. unique identity
##       name for route
##   direction_id: "direction" either 0 or 1,
##       sorta like railroad chaining N or S
##   trip_headsign: nice string to describe 
##       trip direction/destination
##   shape_id: unclear, likely corresponds with 
##       something in shapes_list
##   service_id: unclear, likely corresponds 
##       with calendar date, for service type
##       like "weekend" or "weekday" service
##       *more notes on this: 
##       service starting with A is for the A
##       division. B for B division and R for
##       the SIR. 
##   trip_id: unclear, likely the unique ID
##       for this exact trip
#################################################
## Stop Times List:
#stop_times_list = getDictList(stop_times)
## Field Descriptions:
##   pickup_type: Not totally sure, for an N
##       Train to Astoria, it's 1 for initial
##       Stops (till 8th ave) and then 0 after.
##       Also it's zero for the first stop. 
##       My guess: it's a yes/no on is the train
##       picking up passengers "only" i.e. for
##       the first few stops...
##   stop_headsign: Always Blank
##   shape_dist_traveled: Always Blank
##   arrival_time: How many minutes, into the
##       run of the train does this stop happen
##       for a given trip, does not necessairily
##       start at zero, likely because it's a 
##       "turned train" from another trip
##       #more notes on arrival time:
##       arrival times are not done on 24h clock
##       a train leaving a terminal at 23:50
##       counts up past 24, 25, 26 or even 27:00
##       rather than going back down to zero
##       this could make it easier to subtract
##       as cycle errors are not an issue
##   stop_sequence: at what point in the trip
##       is this stop, (1,2,3,4,5,...) starts
##       at 1 for initial stop
##   stop_id: same stop ID as from stop_list
##       uniquely identifies a stop
##   drop_off_type: Always same as pickup_type
##   trip_id: Same trip ID as from trip_list
##   departure_time: same as arrival time
#################################################
## Transfers List:
#transfers_list = getDictList(transfers)
## Field Descriptions:
##   transfer_type: Always '2'
##   min_transfer_time: 300,180,120,90,0
##       stops list transfers to themselves,
##       x-platform xfers are weighted zero
##   to_stop_id: stop_list id of the stop
##   from_stop_id: stop_list id of other stop
##       to and from do double listing i.e.
##       for A<->B transfer we get
##       A->A, A->B, B->A, B->B
#################################################
## Calendar  List: 
#calendar_list = getDictList(calendar)
## Field Descriptions:
##   end_date: always 20161231 (december 31)
##   monday: binary '1' or '1' if schedule is
##       active on monday
##   tuesday: same binary as monday
##   wednesday: same binary as monday
##   thursday: same binary as monday
##   friday: same binary as monday
##   saturday: same binary as monday
##   sunday: same binary as monday
##   start_date: maybe start/end is improperly
##       used? start day is either may 10 2015 
##       or dec 06 2015, end day is always dec16
##   service_id: ID of the service day
##       starts with A or B for the 1206 scheduls
##       starts with R for 0510 schedules. 
#################################################
## Calendar Dates List: 
#calendar_dates_list = getDictList(calendar_dates)
## Field Descriptions:
##   date: YYYYMMDD
##   service_id: Refrence to service ID from 
##       calendar_list
##   exeption_type: either '1' or '2', 
##       1: says this date, will have this serv
##       pattern even though it's the wrong DOW
##       2: says this date will not have this
##       service pattern even though it's 
##       true in general. 
##       Typically a holiday falling on a monday
##       or friday gets a 1- exception for the 
##       new service pat(satsun) and a 2 excep
##       nixing the old service pattern (wkd) 
#################################################
## Shapes List:
#shapes_list = getDictList(shapes)
## Field Descriptions:
##   shape_pt_lat: lat of shape point
##   shape_pt_lon: lon of shape point
##   shape_id: corresponds to trip_list shape_id
##   shape_pt_sequence: ordering of points to 
##       draw shape correctly
##   shape_dist_traveled: always blank 
#################################################

#################################################
## Create the object Databases
#################################################
def makeObjectDB(verbose=False, force=False,
        extra_transfer=True):
  if checkForDB(dbname):
    print('DB already exists')
    if not force:
      print('To force creation of new DB either')
      print('delete {0}'.format(dbname))
      print('or run makeObjectDB(force=True)')
      return
    else:
      print('overwriting existing DB')
      os.remove(dbname)
  print('Creating new Database')
  #first, get our lists
  if verbose: print('Reading in Files: ',end="")
  route_list = getDictList(routes)
  stop_list = getDictList(stops)
  trip_list = getDictList(trips)
  stop_times_list = getDictList(stop_times)
  transfers_list = getDictList(transfers)
  calendar_list = getDictList(calendar)
  extra_transfers_list = getDictList(extra_transfers)   
  if verbose: print('Done')
  #next, turn lists into objects
  db.connect()
  db.create_tables([Route,Stop,Trip,
      StopTime, Transfer])

  if verbose: print(
      'Creating Routes:    ',end="")
  for i,r in enumerate(route_list):
    robj = Route(name = r['route_long_name'],
        route_id = r['route_id'])
    robj.save()
    if verbose:
      percent = (i*100)/len(route_list)
      print('\b\b\b{0:2}%'.format(percent),
          end="")
  if verbose: print('\b\b\bDone  ')

  if verbose: print(
      'Creating Stops:    ',end="")
  for i,s in enumerate(stop_list):
    if s['location_type'] == '1': #parent
      sobj = Stop(name = s['stop_name'],
          stop_id = s['stop_id'])
      sobj.save()
    if verbose:
      percent = (i*100)/len(stop_list)
      print('\b\b\b{0:2}%'.format(percent),
          end="")
  if verbose: print('\b\b\bDone  ')
  
  if verbose: print(
      'Creating Trips:    ',end="") 
  for i,t in enumerate(trip_list):
    if 'Weekday' not in t['service_id']: continue
    r = Route.get(
        Route.route_id == t['route_id'])
    north = (t['direction_id'] == '1')
    tobj = Trip(route = r, 
        direction = north,
        name = t['trip_headsign'],
        schedule = t['service_id'],
        trip_id = t['trip_id'])
    tobj.save()
    if verbose:
      percent = (i*100)/len(trip_list)
      print('\b\b\b{0:2}%'.format(percent),
          end="")
  if verbose: print('\b\b\bDone  ')

  if verbose: print(
      'Creating StopTimes:    ',end="")
  for i,st in enumerate(stop_times_list):
    if 'Weekday' not in st['trip_id']: continue
    if st['stop_id'][-1] in ('N','S'):
      stop_id = st['stop_id'][:-1]
    else: 
      stop_id = st['stop_id']
    s = Stop.get(Stop.stop_id == stop_id)
    t = Trip.get(Trip.trip_id == st['trip_id'])
    arr = convertTime(st['arrival_time'])
    sq = int(st['stop_sequence'])
    stobj = StopTime(time = arr, seq = sq, 
        stop = s, trip = t)
    stobj.save()
    if verbose:
      percent = (i*100)/len(stop_times_list)
      print('\b\b\b{0:2}%'.format(percent),
          end="")
  if verbose: print('\b\b\bDone  ')

  if verbose: print(
      'Creating Transfers:    ',end="")
  for i,tr in enumerate(transfers_list):
    if tr['to_stop_id'] == tr['from_stop_id']:
      continue
    st = Stop.get(
         Stop.stop_id==tr['to_stop_id'])
    sf = Stop.get(
         Stop.stop_id == tr['from_stop_id'])
    hms = secondsToHMS(tr['min_transfer_time'])
    trobj = Transfer(time=hms, to=st, frm=sf)
    trobj.save()
    if verbose:
      percent = (i*100)/len(transfers_list)
      print('\b\b\b{0:2}%'.format(percent),
          end="")
  if extra_transfer:
    for i,tx in enumerate(extra_transfers_list):
      st = Stop.get(
          Stop.stop_id==tx['stopA'])
      sf = Stop.get(
          Stop.stop_id==tx['stopB'])
      g_maps_minutes = tx['time']
      adjusted_seconds = int(int(g_maps_minutes)*60*.666/30)*30
      print('adding transfer: {0}'.format(adjusted_seconds))
      hms = secondsToHMS(str(adjusted_seconds))
      txobjA = Transfer(time=hms, to=st, frm=sf)
      txobjB = Transfer(time=hms, to=sf, frm=st)
      txobjA.save()
      txobjB.save()
  if verbose: print('\b\b\bDone  ')
  db.close()
  print('DB Ready')

#given a stop code and a time, and a direction,
# print out the rest of the trip
def printTrip(stop, tim, direction):
  s = Stop.get(Stop.stop_id==stop)
  t = datetime.strptime(tim,'%H:%M:%S')
  t = time(hour=t.hour,minute=t.minute,second=t.second)
  st = StopTime.select().where(StopTime.stop==s).order_by(StopTime.time)
  for stop in st:
    if stop.time >= t and stop.trip.direction==direction:
      myst = stop
      break
  for st in StopTime.select().where(StopTime.trip==myst.trip).order_by(StopTime.seq):
    if st.seq >= myst.seq:
      print('{0} - {1} - {2}'.format(st.time, st.stop.stop_id, st.stop.name))

  

#To find all shortest paths between stops, we
# need adjacencys translated into a dict graph
# i.e. dg[stop_a][stop_b] = trip_time for adj stops
def makeDictGraph(force=False, verbose=False, 
    transfer=330): #two minute transfer penalty def
  if checkForDB(dbname):
    if verbose: print('{0} exists'.format(dbname))
  else:
    if verbose: 
      print('{0} does not exist'.format(dbname))
      print('creating this db first')
    makeObjectDB(verbose=verbose)
      
  if checkForDB(graphname):
    if verbose: print('Graph Already exists')
    if not force:
      if verbose:
        print('To force creation of new graph either')
        print('delete {0}'.format(graphname))
        print('or run generateDictGraph(force=True)')
      return pickle.load(open(graphname, 'rb'))
    else:
      if verbose: print('overwriting existing graph')
      os.remove(graphname)
  if verbose:
    print('Generating Dictionary Graph: ')
    l = len(nyctStops())
  g = {}
  for i,stop in enumerate(nyctStops()):
    if verbose: print(
        '\033[F\033[29C{0}%'.format(str((i*100)/l)))
    g[stop.stop_id] = {}
    for adj in stop.adjacent(xfer=transfer):
      stop_id = str(adj[0])
      time = adj[1].seconds
      g[stop.stop_id][stop_id] = time
  if verbose:
    print('\033[F\033[29C100%')
    print('Saving Graph as pickle {0}'.format(
        graphname))
  pickle.dump(g, open(graphname, 'wb'))
  return g

# Find all shortest paths and return it as a dict
def makeShortestPathsDict(
    force=False, verbose=False):
  if checkForDB(shortest_pathsname):
    if verbose: print('{0} exists'.format(
        shortest_pathsname))
    if not force:
      if verbose: 
        print('To force creation of new dict either')
        print('delete {0}'.format(shortest_pathsname))
        print('or makeShortestPathsDict(force=True)')
      return pickle.load(
          open(shortest_pathsname, 'rb'))
    else:
      if verbose: print('overwriting existing dict')
      os.remove(shortest_pathsname)
  if verbose:
    print('generating shortest paths dict')
    print('')
  d = {} 
  g = makeDictGraph()
  l = len(nyctStops())
  for i,stop in enumerate(nyctStops()):
    if verbose: print(
      '\033[F{0}%'.format(str((i*100)/l)))
    frm = str(stop.stop_id)
    d[frm] = {}
    for j,tostop in enumerate(nyctStops()):
      to = str(tostop.stop_id)
      try:
        d[frm][to] = shortestPath(g,frm,to)
      except KeyError:
        pass
  if verbose: 
    print('\033[F100%')
    print('Saving dict as pickle {0}'.format(
        shortest_pathsname))
  pickle.dump(d, open(shortest_pathsname, 'wb'))
  return d

def makeAdjacencyMatrix():
  def addDummyPoint(matrix, d):
    matrix.append([0]*(len(matrix)))
    for row in matrix:
      row.append(0)
    d['XXX'] = {}
    for stopx in d:
      d[stopx]['XXX']=([stopx,'XXX'],0)
      d['XXX'][stopx]=(['XXX',stopx],0)
    return matrix ,d
  d = makeShortestPathsDict()
  matrix = []
  for i, stopx in enumerate(nyctStops()):
    row = []
    for j, stopy in enumerate(nyctStops()):
      x = stopx.stop_id
      y = stopy.stop_id
      try:
        row.append(d[x][y][1])
      except KeyError:
        pass
    matrix.append(row)
  return addDummyPoint(matrix, d)

def printTSP():
  m, d = makeAdjacencyMatrix()

  route = solve_tsp(m)
  lookup = nyctStops() #for index lookup
  xxx = Stop(name='End of trip', stop_id='XXX')
  xxx.save()
  lookup.append(xxx)
  print(route)
  rotary = []
  for i in range(len(route)):
    a = lookup[route[i]]
    b = lookup[route[(i+1)%len(route)]]
    for stop_code in d[a.stop_id][b.stop_id][0][:-1]:
      st = Stop.get(Stop.stop_id==stop_code)
      #print('{0} - {1}'.format(st.stop_id, st.name))
      rotary.append(st)
  finished = False
  i=0
  printing = False
  sumtime = 0
  rotary.reverse()
  while not finished:
    st = rotary[i]
    stp1=rotary[(i+1)%len(rotary)]
    i += 1
    i = i%len(rotary)
    if printing:
      tim = d[st.stop_id][stp1.stop_id][1]
      sumtime += tim
      print('{2} - {0} - {1}'.format(
          st.stop_id, st.name,secondsToHMS(sumtime)))
    if st.stop_id == 'XXX':
      if printing == False:
        printing = True
      else:
        finished = True
  xxx.delete_instance()

#printTSP()
