#This will be a series of functions.
# Each function returns "True" if the stop is 
# a member of given "Branch" and false otherwise
# Wherever possible this will be done with stop code arithmetic

#Splits a stop code into a line, and an int
def digestStopCode(c):
	return c[0],int(c[1:])

##all this using lambdas
# f will take a line code and range. 
# it will return an anonymous function that takes a 
# stop code and returns whether or not it's in the given range
def f(line,rangeL,rangeH):
	return lambda c:c[0]==line and rangeL<=int(c[1:])<=rangeH

lines = [
	f('1',1,19),		#1 Above 96st
	f('1',20,37),		#1 Btw 96 and Chambers
	f('1',38,42),		#1 South of Chambers
	f('2',4,12),		#2 Above E180
	f('2',13,22),		#2 Btw E180 and 149GC
	f('2',24,27),		#2 Btw 135 and 110
	f('2',28,39),		#2 Btw Park pl and Franklin
	f('2',41,47),		#2 South of Franklin
	f('3',1,2),			#3 148 and 145
	f('2',48,57),		#3 East of Franklin
	f('4',1,15),		#4 North of 149GC
	f('5',1,5),			#5 North of E180
	f('6',1,19),		#6 North of 125
	lambda c:f('6',21,40)(c) or f('4',18,23)(c),	#6 125 to Boro Hall
	f('7',0,100),		#7 All
	f('9',0,100),		#GC Shuttle
	f('A',2,11),		#A north of 145
	lambda c:f('A',12,24)(c) or f('D',13,13)(c),	#A 145 to 59
	lambda c:f('A',25,34)(c) or f('D',20,20)(c),	#A 50 to Canal
	f('A',36,40),		#A Chambers to High
	f('A',43,61),		#A Lafyette to Rockaway blvd
	f('A',63,65),		#A Liberty line
	f('H',1,4),			#A Aqueduct to Broad Channel
	f('H',6,11),		#A Beach 67 to Far Rock
	f('H',12,15),		#A Beach 90 to Rock Park
	f('D',3,12),		#D Concourse 
	lambda c:f('D',15,21)(c) or f('A',32,32)(c),	#D Sixth av
	f('R',31,36),		#D Fourth ave D section
	lambda c:f('B',12,23)(c) or f('D',43,43)(c),	#D West End
	f('G',5,6),			#E Archer ave ext
	lambda c:f('F',5,7)(c) or f('G',8,20)(c),		#E local QBL
	f('F',9,12),		#E 53st Tunnel
	f('F',1,4),			#F hillside ave ext
	f('B',4,10),		#F 63rd st tunnel
	f('F',14,18),		#F Lower East Side
	f('F',20,39),		#F Culver
	f('D',42,43),		#F Coney and Aquarium
	f('G',22,36),		#G crosstown
	f('J',12,31),		#J Jamaica to Myrtle
	f('M',11,18),		#J Myrtle to Essex
	f('M',19,23),		#J Centre
	f('L',0,100),		#L All
	f('M',1,10),		#M Metropolitan to Myrtle
	f('R',1,8),			#N Astoria
	f('R',11,13),		#N 59th st tunnel
	f('R',14,22),		#N Broadway
	f('R',24,29),		#N Lower Broadway
	f('R',39,41),		#N Mid fourth ave
	lambda c:f('N',2,10)(c) or f('D',43,43)(c),		#N Sea Beach
	f('Q',3,5),			#Q Second ave
	f('D',24,41),		#Q Brighton
	lambda c:f('S',1,3)(c) or f('D',26,26)(c),		#S Franklin
	f('R',42,45),		#R Bay Ridge
	f('S',9,31),		#SIR
]

def sameLine(s1,s2):
	if len(s1) != 3 or len(s2) != 3: raise ValueError
	for l in lines:
		if not l(s1): continue
		if l(s2): return True
	return False
