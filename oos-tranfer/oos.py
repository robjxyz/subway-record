import csv

#take a list of headers, and a row. 
#return a dict {h[0]:r[0],h[1]:r[1]...}
def pack(header, row):
    d = {}
    for i in range(len(header)):
        d[header[i]]=row[i]
    return d

with open("StationEntrances.csv") as f:
    reader = csv.reader(f)
    header = next(reader)
    data = [pack(header,r) for r in reader]
    print(len(data))
    print(data[0])

