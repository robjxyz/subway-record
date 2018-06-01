# subway-record
Directory contains two  foldes: 

concorde-for-subway
Concorde is a C program used to solve TSP and other similar problems. It's 
somewhat complex to set up, but it's powerful. Inside it is a readme explaining
further. 

robs-old-tsp
Contains data from rob's old attempt to solve the problem with tsp. 
To build the infrastructure, run subCalc.py. Stop+stoptime info is stored in
text files from MTA's open data portal, modifying this requires rebuilding 
subway.db (a peewee database). The adjacency matrix is stored in graph.p
(pickled dictionary), this must be rebuilt if the subway.db is rebuilt. 

