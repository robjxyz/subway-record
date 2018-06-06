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
	for o in range(len(j['origin_addresses'])):
		print('  {0}  {1}'.format(str(o),j['origin_addresses'][o]))
	print('Destinations:')
	for d in range(len(j['destination_addresses'])):
		print('  {0}  {1}'.format(chr(ord('A')+d),j['destination_addresses'][d]))
def gmapsRequest(s1,s2):
	origin = origDestString(s1)
	dest = origDestString(s2)
	key = ''
	units = 'imperial'
	mode = 'walking'
	url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
	request = '{0}units={1}&mode={2}&origins={3}&destinations={4}&key={5}'.format(
		url,units,mode,origin,dest,key)
	#return requests.get(url=request).json()
	return {'origin_addresses': ['1312 55th St, Brooklyn, NY 11219, USA', '5501 Raoul Wallenberg Way, Brooklyn, NY 11219, USA', '5415-5417 New Utrecht Ave, Brooklyn, NY 11219, USA'], 'destination_addresses': ['Rockaway Fwy, Far Rockaway, NY 11691, USA', 'Rockaway Fwy, Far Rockaway, NY 11691, USA', 'Rockaway Fwy, Far Rockaway, NY 11691, USA', 'Rockaway Fwy, Far Rockaway, NY 11691, USA'], 'rows': [{'elements': [{'duration': {'text': '5 hours 3 mins', 'value': 18153}, 'distance': {'text': '15.2 mi', 'value': 24527}, 'status': 'OK'}, {'duration': {'text': '5 hours 2 mins', 'value': 18105}, 'distance': {'text': '15.2 mi', 'value': 24489}, 'status': 'OK'}, {'duration': {'text': '5 hours 2 mins', 'value': 18131}, 'distance': {'text': '15.2 mi', 'value': 24497}, 'status': 'OK'}, {'duration': {'text': '5 hours 2 mins', 'value': 18128}, 'distance': {'text': '15.2 mi', 'value': 24520}, 'status': 'OK'}]}, {'elements': [{'duration': {'text': '5 hours 3 mins', 'value': 18203}, 'distance': {'text': '15.3 mi', 'value': 24583}, 'status': 'OK'}, {'duration': {'text': '5 hours 3 mins', 'value': 18156}, 'distance': {'text': '15.3 mi', 'value': 24545}, 'status': 'OK'}, {'duration': {'text': '5 hours 3 mins', 'value': 18181}, 'distance': {'text': '15.3 mi', 'value': 24552}, 'status': 'OK'}, {'duration': {'text': '5 hours 3 mins', 'value': 18178}, 'distance': {'text': '15.3 mi', 'value': 24575}, 'status': 'OK'}]}, {'elements': [{'duration': {'text': '5 hours 3 mins', 'value': 18174}, 'distance': {'text': '15.3 mi', 'value': 24556}, 'status': 'OK'}, {'duration': {'text': '5 hours 2 mins', 'value': 18127}, 'distance': {'text': '15.2 mi', 'value': 24519}, 'status': 'OK'}, {'duration': {'text': '5 hours 3 mins', 'value': 18152}, 'distance': {'text': '15.2 mi', 'value': 24526}, 'status': 'OK'}, {'duration': {'text': '5 hours 2 mins', 'value': 18149}, 'distance': {'text': '15.3 mi', 'value': 24549}, 'status': 'OK'}]}], 'status': 'OK'}


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

stopone = random.choice(stations)
stoptwo = random.choice(stations)

#printStop(stopone)
#for e in getAllEnts(stopone):
#	printEnt(e)
#printStop(stoptwo)
#for e in getAllEnts(stoptwo):
#	printEnt(e)
#r = requests.get(url=gmapsDistance(stopone,stoptwo))
#data = r.json()
printGmaps(gmapsRequest(stopone,stoptwo))
