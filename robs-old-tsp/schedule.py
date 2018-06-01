from subLib import *

#print(Route.get(route_id='A').name)
#listLineStops('A')
#printTrip('H11','02:00:00',False)

#Takes a stoptime object, 
#finds the possibilities: 
# R(ide), W(ait), X(fer)
# returns a list of tuples (stoptime, rwx) 
# this list is variable length because: 
#  there could be multiple Xfers and
#  at terminals, Ride is not an option
def rwx(current):
  ride = nextRide(current)
  wait = nextWait(current)
  if ride:
    return [ride,wait]
  return [wait]

def nextRide(current):
  try:
    return StopTime.get(
        StopTime.seq==current.seq+1,
        StopTime.trip==current.trip)
  except:
    return

def nextWait(current):
  allAtStop = StopTime.select().where(
      StopTime.stop==current.stop).order_by(StopTime.time)
  for s in allAtStop:
    if s.time<=current.time:
      continue
    return s
  return allAtStop[0]

def printST(st):
  print('{0} - {1} - {2}'.format(st.trip.route.route_id,st.stop.name,st.time))

testStop = Stop.get(Stop.stop_id=='A12')
testST = StopTime.select().where(
    StopTime.stop==testStop)[0]
#print(testST.time)
#print(testST.seq)
#print(testST.trip.name)
printST(testST)
print('------------------------------')

#checks a level for new stops,
# returns the path to that stop
def findNew(level,visited):
  for node in level:
    if node[-1].stop not in visited:
      return node
  return findNew(nextLevel(level),visited)

#"level" is a list of stoptime lists, denoting 
#  a level of a tree. 
def nextLevel(level):
  nextlevel = []
  for node in level:
    current = node[-1]
    for nextnode in rwx(current):
      nextlevel.append(node+[nextnode])
  return nextlevel


c = testST
visitedStops = [c.stop]
route = [c]
for i in range(60):

  current = route[-1]
  new = findNew([[current]],visitedStops)
  for s in new[1:]:
    visitedStops.append(s.stop)
    route.append(s)
  printST(route[-1])
