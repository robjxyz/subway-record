from stationtools import *


#Check if a stop tuple (s1,s2) is in a list already. For transfers list
def inList(tup,l):
	for item in l:
		if item[0] == tup:
			return True
		if (item[0][1],item[0][0]) == tup:
			return True
	return False

#get a transfer list from pickle
try: 
	transfers = pickle.load(open("transfers-oos.pickle","rb"))
except (OSError, IOError) as e:
	transfers = []

#Save transfers to transfer list T
#only save r more
def saveTransfers(t,r):
	requests = 0
	for s1 in stations:
		if s1['Division']=='SIR':continue
		if s1['GTFS Stop ID']=='138':continue #cortlandt
		for s2 in stations:
			if s2['Division']=='SIR':continue
			if s2['GTFS Stop ID']=='138':continue
			if sameLine(s1['GTFS Stop ID'],s2['GTFS Stop ID']):continue
			if inList((s1['GTFS Stop ID'],s2['GTFS Stop ID']),t):continue
			d = geoDistance(
				(s1['GTFS Latitude'],s1['GTFS Longitude']),
				(s2['GTFS Latitude'],s2['GTFS Longitude']))
			if d<3500:
				print('{0}({1})\t{2}({3})'.format(
					s1['Stop Name'],s1['Daytime Routes'],
					s2['Stop Name'],s2['Daytime Routes']))
				try:
					gmapsd = lazyGmapsMin(s1,s2)
				except IndexError:
					print('Error Error Error ----------------------------------------')
					continue
				t.append(((s1['GTFS Stop ID'],s2['GTFS Stop ID']),gmapsd))
				requests += 1
				if requests >= r: return
			
#make an "extra transfers" file
def extraTransfers(path):
	with open(path,'w+') as f:
		f.write('stopA,stopB,distance,time,comments\n')
		for t in transfers:
			stopA = t[0][0]
			stopB = t[0][1]
			distance = t[1]*.000621371
			time = distance*9
			f.write('{0},{1},{2},{3},\n'.format(stopA,stopB,round(distance,1),round(time)))
			

extraTransfers('/home/robj/Scripts/subway-record/oos-tranfer/extra.txt')

#saveTransfers(transfers,2400)
#for l in transfers:
#	print(l)
#print('Saved '+str(len(transfers)))

#pickle.dump(transfers,open("transfers-oos.pickle","wb"))


#stopone = lookupStation('108')#random.choice(stations)
#stoptwo = lookupStation('A02')#random.choice(stations)
#
#for row in gmapsRequest(stopone,stoptwo):
#	print(row)
#print('')
#for row in geoRequest(stopone,stoptwo):
#	print(row)
#print(geoMin(stopone,stoptwo)[2])
#print(lazyGmapsMin(stopone,stoptwo))
