import csv,random,json,requests,geopy.distance,pickle
from lineDef import sameLine


#################################################
##  MTA Stop Info Utilities
##   These utilities help digest the csv files from the MTA
##   and create two lists of dictionaries:
##   stations- containing 472 (+Staten Island) stations from Stations.csv
##   stationentrances - containing the +1k station entrances
#################################################

#take a list of headers, and a row. 
#return a dict {h[0]:r[0],h[1]:r[1]...}
def pack(header, row):
    d = {}
    for i in range(len(header)):
        d[header[i]]=row[i]
    return d
#Ingest Stations.csv and StationEntrances.csv. 
# Return them as lists of dicts
def loadCSV():
	stations = []
	with open("Stations.csv") as f:
	    reader = csv.reader(f)
	    header = next(reader)
	    stations = [pack(header,r) for r in reader]
	entrances = []
	with open("StationEntrances.csv") as f:
	    reader = csv.reader(f)
	    header = next(reader)
	    entrances = [pack(header,r) for r in reader]
	for ent in entrances:
		ent['Stop ID']=stationCode(ent,stations)
	return stations,entrances
#Given an original "Enrance" row, find the corresponding
# station code using the gps coordinate match from "Stations"
def stationCode(e,stations):
	for s in stations:
		if s['GTFS Latitude'] == e['Station_Latitude']:
			if s['GTFS Longitude'] == e['Station_Longitude']:
				return(s['GTFS Stop ID'])

#Given a station row, find the corresponding Entrances, return as a list
def getEnts(s):
	ents = []
	for e in entrances:
		if e['Stop ID'] == s['GTFS Stop ID']:
			ents.append(e)
	return ents
#Given a station row, find any stations in its station complex
def getComplex(s):
	cplx = []
	for sta in stations:
		if s['Complex ID'] == sta['Complex ID']:
			cplx.append(sta)
	return cplx
#Given a staion row, find all entrances in the corresponding station
# and all entrances in the stations's complex
# If given an entrance, return that entrance. This allows us to feed
# gmaps request entrances directly without modifying the code
def getAllEnts(s):
	if s in entrances:
		return [s] 
	allEnts = []
	for sta in getComplex(s):
		allEnts += getEnts(sta)
	return allEnts
#given a Stop ID, return the Station dict
def lookupStation(code):
	for s in stations:
		if s['GTFS Stop ID'] == code:
			return s
	return None

#############################################################
##  Manual Distance Functions
#############################################################

#Takes two lat,lon tuples, gives a distance in m
#  as-the-crow-flies
def geoDistance(p1,p2):
	return round(geopy.distance.vincenty(p1,p2).m)
#Takes two station dicts and makes a matrix of all the geometric
# distances between their complexes entrances and exits
# returns a double list
def geoRequest(s1,s2):
	orig = getAllEnts(s1)
	dest = getAllEnts(s2)
	distanceMatrix = []
	for o in orig:
		row = []
		for d in dest:
			row.append(geoDistance(
				(o['Latitude'],o['Longitude']),
				(d['Latitude'],d['Longitude'])))
		distanceMatrix.append(row)
	return distanceMatrix
#Takes two stops, finds their entrances, compares all with 
# geometric distance. Returns the two closest, and the 
# corresponding distance
def geoMin(s1,s2):
	orig = getAllEnts(s1)
	dest = getAllEnts(s2)
	bestorig=orig[0]
	bestdest=dest[0]
	bestdist=100000
	for o in orig:
		for d in dest:
			newDist = geoDistance(
				(o['Latitude'],o['Longitude']),
				(d['Latitude'],d['Longitude']))
			if newDist <= bestdist:
				bestorig = o
				bestdest = d
				bestdist = newDist
	return bestorig,bestdest,bestdist
#############################################################
## Google Maps Distance Functions
#############################################################

#Takes a station, gets its entrances, returns a google maps suitable
# string for use with their API. 
def origDestString(s):
	ents = getAllEnts(s)
	return ''.join(['{0}%2C{1}%7C'.format(e['Latitude'],e[
		'Longitude']) for e in ents])[:-3]
#Takes two station dicts, finds coordinates of all their entrances 
# and exits, and sends that through the google maps distance-matrix
# API. This is done by assembling the URL and then using requests.get
# Now it returns a funny JSON object. in the future it should return a 
# distance matrix like the geometric one does.
# 
# origDestString has been modified so that it can accept entrances
# as well as stations, if given an entrance it returns that single 
# entrance. This allows gmaps to accept single entrance/exit pairs
# as well as entire stations
def gmapsRequest(s1,s2):
	origin = origDestString(s1)
	dest = origDestString(s2)
	key = ''
	units = 'imperial'
	mode = 'walking'
	url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
	request = '{0}units={1}&mode={2}&origins={3}&destinations={4}&key={5}'.format(
		url,units,mode,origin,dest,key)
	#print(request)
	j =  requests.get(url=request).json()
	distanceMatrix = []
	for o in j['rows']:
		row = []
		for d in o['elements']:
			row.append(d['distance']['value'])
		distanceMatrix.append(row)
	return distanceMatrix
#print out the gmaps request JSON nicely
#def printGmaps(j):
#	print('Origins:')
#	for o,origin in enumerate(j['origin_addresses']):
#		print('  {0}  {1}'.format(str(o),origin))
#	print('Destinations:')
#	for d,destination in enumerate(j['destination_addresses']):
#		print('  {0}  {1}'.format(chr(ord('A')+d),destination))
#	print('')
#	s = '           '
#	for d in range(len(j['destination_addresses'])):
#		s+='{0:8}'.format(str(chr(ord('A')+d)))
#	print(s)
#	for r,row in enumerate(j['rows']):
#		s = ''
#		s+='   {0} '.format(int(r))
#		for element in row['elements']:
#			s+='{0:8}'.format(element['distance']['value'])
#		print(s)
#	print('')
#Takes two stations, runs them through the geometric min 
# to ascertain which entrances are cloest, then runs the min
# entrance pair through gmaps. This is to place only one
# element request on gmaps per station pairing
def lazyGmapsMin(s1,s2):
	orig,dest,dist = geoMin(s1,s2)
	return gmapsRequest(orig,dest)[0][0]

##########################################################
## Pretty print functions
#########################################################
#print a stops details nicely
def printStop(s):
	print('{0} - {1}, {2}'.format(s['Stop Name'],s['GTFS Stop ID'],
		s['Daytime Routes']))
#print an entrances details nicely
def printEnt(e):
	print('{0} {1},{2},{3}'.format(e['Stop ID'],
		e['North_South_Street'],e['East_West_Street'],e['Corner']))	


#Check if a stop tuple (s1,s2) is in a list already. For transfers list
#def inList(tup,l):
#	for item in l:
#		if item[0] == tup:
#			return True
#		if (item[0][1],item[0][0]) == tup:
#			return True
#	return False
#	
#
##get a transfer list from pickle
#try: 
#	transfers = pickle.load(open("transfers-oos.pickle","rb"))
#except (OSError, IOError) as e:
#	transfers = []
#
##Save transfers to transfer list T
##only save r more
#def saveTransfers(t,r):
#	requests = 0
#	for s1 in stations:
#		if s1['Division']=='SIR':continue
#		for s2 in stations:
#			if s2['Division']=='SIR':continue
#			if sameLine(s1['GTFS Stop ID'],s2['GTFS Stop ID']):continue
#			#if inList((s1['GTFS Stop ID'],s2['GTFS Stop ID']),t):continue
#			d = geoDistance(
#				(s1['GTFS Latitude'],s1['GTFS Longitude']),
#				(s2['GTFS Latitude'],s2['GTFS Longitude']))
#			if d<3500:
#				print('{0}({1})\t{2}({3})'.format(
#					s1['Stop Name'],s1['Daytime Routes'],
#					s2['Stop Name'],s2['Daytime Routes']))
#				t.append(((s1['GTFS Stop ID'],s2['GTFS Stop ID']),d))
#				requests += 1
#				if requests >= r: return
#			
#
####################################################
##  Main: This loads the CSVs so it works when you import this
####################################################
stations,entrances = loadCSV()
