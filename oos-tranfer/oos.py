import csv

#take a list of headers, and a row. 
#return a dict {h[0]:r[0],h[1]:r[1]...}
def pack(header, row):
    d = {}
    for i in range(len(header)):
        d[header[i]]=row[i]
    return d

entrances = []
with open("StationEntrances.csv") as f:
    reader = csv.reader(f)
    header = next(reader)
    entrances = [pack(header,r) for r in reader]

stations = []
with open("Stations.csv") as f:
    reader = csv.reader(f)
    header = next(reader)
    stations = [pack(header,r) for r in reader]

print(len(entrances))
print(entrances[0])

print(len(stations))
print(stations[0])

def stationCode(e):
    print(e['Station_Name'])
    print(e['Station_Latitude'])
    print(e['Station_Longitude'])
    for s in stations:
        if s['GTFS Latitude'] == e['Station_Latitude']:
            if s['GTFS Longitude'] == e['Station_Longitude']:
                return(s['GTFS Stop ID'])

for ent in entrances:
  print(stationCode(ent))
