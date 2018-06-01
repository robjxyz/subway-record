from __future__ import print_function, generators #gen from prioridict
import os.path, time, datetime, sys, pickle
import subLib
from subLib import Route, Stop, Trip
from subLib import StopTime, Transfer
#from tsp_solver.greedy import solve_tsp

db = subLib.SqliteDatabase(subLib.dbname)   

#def nextNDepartures(stop, time, n, display=False):
#  stopTimes = StopTime.select().where((StopTime.stop==stop) & (StopTime.time > time)).order_by(StopTime.time)[:n]
#  if display:
#    print('Departures from: {0} ({1})'.format(stop.name,stop.stop_id))
#    for d in stopTimes:
#      print('{0}- ({1}) {2}'.format(d.time,d.trip.route.route_id,d.trip.name))
#  return stopTimes

#def searchStopCodes(longName):
#  stops = Stop.select().where(Stop.name==longName)
#  codes = []
#  for s in stops:
#    codes.append((s.stop_id, s.name))
#  return codes


#Will this train, go to my desired stop?
#def onRoute(start, end, trip):
#  startseq = StopTime.get((StopTime.trip==trip) & (StopTime.stop==start)).seq
#  endseq = StopTime.get((StopTime.trip==trip) & (StopTime.stop==end)).seq
#  return startseq <= endseq
  
#def timeTrip(start, end, startTime, showstops=False):
#  nextStopTimes = nextNDepartures(start, startTime, 10)
#  for potentialTrip in nextStopTimes:
#    startst = StopTime.get((StopTime.trip==potentialTrip.trip) & (StopTime.stop==start))
#    endst = StopTime.get((StopTime.trip==potentialTrip.trip) & (StopTime.stop==end))
#    if startst.seq <= endst.seq:
#      endTime = endst.time
#      time = subtractTimes(endTime,startTime)
#      print('Next trip from {4}({0}) to {5}({1}) \nwill take {2} and arrive at {3}'.format(
#          start.stop_id, end.stop_id, time, endTime, start.name, end.name))
#      if showstops:
#        stops = StopTime.select().where(StopTime.trip==potentialTrip.trip).order_by(str(StopTime.seq))
#        for s in stops:
#          if int(startst.seq) <= int(s.seq) <= int(endst.seq):
#            print('{0} - {1}({2})'.format(s.time, s.stop.name, s.stop.stop_id))
#      return
#
#return stop_id, [(adj,adj_time),(adj,adj_time),...]


#listLineStops('1',0)
#listLineStops('D',0)
#print(searchStopCodes('Far Rockaway'))
#stop = Stop.get(Stop.stop_id=='213')
#stopb = Stop.get(Stop.stop_id=='225')
#stopc = Stop.get(Stop.stop_id=='G14')
#stopd = Stop.get(Stop.stop_id=='239')
#stope = Stop.get(Stop.stop_id=='401')
#time = '01:00:00'
#timeTrip(stop,stopb,time,showstops=True)
#nextNDepartures(stop,time,10,display=True)
#print(adjacentStops(stope))

#def generateAdjMatrix(verbose=False):
#  if verbose: print('Generating Adjacency matrix')
#  getIndex = {}
#  for i,stop in enumerate(nyctStops()):
#    getIndex[str(stop.stop_id)] = i
#  
#  if verbose: 
#      print('Matrix size {0}x{0}'.format(len(getIndex)))
#  if verbose: 
#      print('Generating: 0% ')
#  
#  completeMatrix=[]
#  for i,stop in enumerate(nyctStops()):
#    if verbose: print(
#        '\033[F\033[12C{0}%'.format(str((i*100)/len(getIndex))))
#    rowDict = {}
#    rowDict[i] = 0 #stop-to-self is dist zero
#    for adj in adjacentStops(stop):
#      stop_id = str(adj[0])
#      stop_index = getIndex[stop_id]
#      time = adj[1].seconds
#      rowDict[stop_index] = time
#    rowList = []
#    for index in range(len(getIndex)):
#      if index in rowDict:
#        rowList.append(rowDict[index])
#      else:
#        rowList.append(36000) #one hour
#    #now we've got us a complete row!
#    completeMatrix.append(rowList)
#  if verbose:
#    print('\033[F\033[12C100%') 
#    print('Adjacency Matrix Complete')
#  return completeMatrix

#def generateDictGraph(force=False,verbose=False,transfer=120):
#  if subLib.checkForPickle(subLib.picklename):
#    if verbose: print('DictGraph Already exists')
#    if not force:
#      if verbose:
#        print('To force creation of new pickle either')
#        print('delete {0}'.format(subLib.picklename))
#        print('or run generateDictGraph(force=True)')
#      return pickle.load(open(subLib.picklename, 'rb'))
#    else:
#      if verbose: print('overwriting existing pickle')
#      os.remove(subLib.picklename)
#  if verbose: 
#    print('Generating Dictionary Graph: ')
#    l = len(nyctStops())
#  g = {}
#  for i,stop in enumerate(nyctStops()):
#    if verbose: print('\033[F\033[29C{0}%'.format(str((i*100)/l)))
#    g[stop.stop_id] = {}
#    for adj in adjacentStops(stop,transferPenalty=transfer):
#      stop_id = str(adj[0])
#      time = adj[1].seconds
#      g[stop.stop_id][stop_id] = time
#  if verbose: 
#    print('\033[F\033[29C100%')
#    print('Saving DictGraph as pickle {0}'.format(subLib.picklename))
#  pickle.dump(g, open(subLib.picklename, 'wb'))
#  return g

#def shortestPathsBetweenAllStops(force=False, verbose=False):
#  if subLib.checkForPickle(subLib.picklename2):
#    if verbose: print('shortestpathdict already exists')
#    if not force:
#      if verbose: 
#        print('To force creation of new pickle either')
#        print('delete {0}'.format(subLib.picklename2))
#        print('or run generateDictGraph(force=True)')
#      return pickle.load(open(subLib.picklename2, 'rb'))
#    else:
#      if verbose: print('overwriting existing pickle')
#      os.remove(subLib.picklename2)
#  if verbose: 
#    print('generating Shortest path matrix')
#    print('')
#  d = {}
#  g = generateDictGraph()
#  l = len(nyctStops())
#  for i,stop in enumerate(nyctStops()):
#    if verbose: print('\033[F{0}%'.format(str((i*100)/l)))
#    frm = str(stop.stop_id)
#    d[frm] = {}
#    for j,tostop in enumerate(nyctStops()):
#      to = str(tostop.stop_id)
#      d[frm][to] = shortestPath(g,frm,to)
#  if verbose: 
#    print('\033[F100%')
#    print('Saving shortestpathdict as pickle {0}'.format(subLib.picklename2))
#  pickle.dump(d, open(subLib.picklename2, 'wb'))
#  return d

#def generateAdjacencyMatrix2():
#  g = shortestPathsBetweenAllStops()
#  matrix = []
#  for i, stopx in enumerate(nyctStops()):
#    row = []
#    for j, stopy in enumerate(nyctStops()):
#      x = stopx.stop_id
#      y = stopy.stop_id
#      row.append(g[x][y][1])
#    matrix.append(row)
#  return matrix, g

def printPath(path):
  stopList = nyctStops()
  for i,p in enumerate(path):
    stop = stopList[p]
    name = stop.name
    stop_id = stop.stop_id
    print('{2} - \t {0}({1})'.format(stop_id, name,i))

def printDijkstra(shortestPathResult):
  path, length = shortestPathResult
  for stop in path:
    obj = Stop.get(Stop.stop_id==stop)
    print('{0} - {1}'.format(obj.stop_id,obj.name))
  print('total length: {0}'.format(length))

d,l = generateAdjacencyMatrix2()

#printPath([0,1,2,3,4])
#d = [[ 0, 1000, 2,1000],
#     [ 1000, 0, 3,1000],
#     [ 2, 3, 0, 2],
#     [1000,1000,2,0]]
#print('Solving TSP, this may take awhile...')
path = solve_tsp(d)
printPath(path)
#print(path)
#g = {'s':{'u':10, 'x':5}, 'u':{'v':1, 'x':2}, 'v':{'y':4}, 'x':{'u':3, 'v':9, 'y':2}, 'y':{'s':7, 'v':6}}
#print(shortestPath(g,'s','v'))
#g = generateDictGraph(verbose=True)

