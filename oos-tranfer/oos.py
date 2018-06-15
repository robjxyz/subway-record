import csv,random,json,requests,geopy.distance
from lineDef import sameLine

#Takes two lat,lon tuples, gives a distance in m
#  as-the-crow-flies
def geoDistance(p1,p2):
	return round(geopy.distance.vincenty(p1,p2).m)

#take a list of headers, and a row. 
#return a dict {h[0]:r[0],h[1]:r[1]...}
def pack(header, row):
    d = {}
    for i in range(len(header)):
        d[header[i]]=row[i]
    return d
#Given an original "Enrance" row, find the corresponding
# station code using the gps coordinate match from "Stations"
def stationCode(e):
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
def getComplex(s):
	cplx = []
	for sta in stations:
		if s['Complex ID'] == sta['Complex ID']:
			cplx.append(sta)
	return cplx
def getAllEnts(s):
	allEnts = []
	for sta in getComplex(s):
		allEnts += getEnts(sta)
	return allEnts
def origDestString(s):
	ents = getAllEnts(s)
	return ''.join(['{0}%2C{1}%7C'.format(e['Latitude'],e[
		'Longitude']) for e in ents])[:-3]
#print a stops details nicely
def printStop(s):
	print('{0} - {1}, {2}'.format(s['Stop Name'],s['GTFS Stop ID'],
		s['Daytime Routes']))
def printEnt(e):
	print('{0} {1},{2},{3}'.format(e['Stop ID'],
		e['North_South_Street'],e['East_West_Street'],e['Corner']))	
#print out the JSON nicely
def printGmaps(j):
	print('Origins:')
	for o,origin in enumerate(j['origin_addresses']):
		print('  {0}  {1}'.format(str(o),origin))
	print('Destinations:')
	for d,destination in enumerate(j['destination_addresses']):
		print('  {0}  {1}'.format(chr(ord('A')+d),destination))
	print('')
	s = '           '
	for d in range(len(j['destination_addresses'])):
		s+='{0:8}'.format(str(chr(ord('A')+d)))
	print(s)
	for r,row in enumerate(j['rows']):
		s = ''
		s+='   {0} '.format(int(r))
		for element in row['elements']:
			s+='{0:8}'.format(element['distance']['value'])
		print(s)
	print('')
def gmapsRequest(s1,s2):
	origin = origDestString(s1)
	dest = origDestString(s2)
	key = ''
	units = 'imperial'
	mode = 'walking'
	url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
	request = '{0}units={1}&mode={2}&origins={3}&destinations={4}&key={5}'.format(
		url,units,mode,origin,dest,key)
	print(request)
	return requests.get(url=request).json()
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

#given a Stop ID, return the Station dict
def lookupStation(code):
	for s in stations:
		if s['GTFS Stop ID'] == code:
			return s
	return None

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
	ent['Stop ID']=stationCode(ent)

requests = 0
for s1 in stations:
	if s1['Division']=='SIR':continue
	if s1['GTFS Stop ID']!='H11':continue
	for s2 in stations:
		if s2['Division']=='SIR':continue
		if sameLine(s1['GTFS Stop ID'],s2['GTFS Stop ID']):continue
		d = geoDistance(
			(s1['GTFS Latitude'],s1['GTFS Longitude']),
			(s2['GTFS Latitude'],s2['GTFS Longitude']))
		if d<3500:
			print('{0}({1})\t{2}({3})'.format(
				s1['Stop Name'],s1['Daytime Routes'],
				s2['Stop Name'],s2['Daytime Routes']))
			requests += 1
print(requests)
		

#stopone = lookupStation('227')#random.choice(stations)
#stoptwo = lookupStation('Q05')#random.choice(stations)

#printStop(stopone)
#for e in getAllEnts(stopone):
#	printEnt(e)
#printStop(stoptwo)
#for e in getAllEnts(stoptwo):
#	printEnt(e)
#r = requests.get(url=gmapsDistance(stopone,stoptwo))
#data = r.json()
#printGmaps(gmapsRequest(stopone,stoptwo))
#for row in geoRequest(stopone,stoptwo):
#	print(row)
#gmapsRequest(stopone,stoptwo)
#print(geoDistance((stopone['GTFS Latitude'],stopone['GTFS Longitude']),
	#(stoptwo['GTFS Latitude'],stoptwo['GTFS Longitude'])))
