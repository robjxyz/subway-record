import csv,random,json,requests

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
			s+='{0:8}'.format(element['duration']['text'])
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
	#print(request)
	return requests.get(url=request).json()
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

stopone = lookupStation('A40')#random.choice(stations)
stoptwo = lookupStation('F18')#random.choice(stations)

printStop(stopone)
#for e in getAllEnts(stopone):
#	printEnt(e)
printStop(stoptwo)
#for e in getAllEnts(stoptwo):
#	printEnt(e)
#r = requests.get(url=gmapsDistance(stopone,stoptwo))
#data = r.json()
printGmaps(gmapsRequest(stopone,stoptwo))
#gmapsRequest(stopone,stoptwo)
