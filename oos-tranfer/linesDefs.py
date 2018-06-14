#This will be a series of functions.
# Each function returns "True" if the stop is 
# a member of given "Branch" and false otherwise
# Wherever possible this will be done with stop code arithmetic

#Splits a stop code into a line, and an int
def digestStopCode(c):
	return c[0],int(c[1:])

#1 train
def bwy7N((code,stop)):
	return code=='1' and 1<=stop<=19
def bwy7M((code,stop)):
	return code=='1' and 20<=stop<=37
def bwy7S((code,stop)):
	return code=='1' and 38<=stop<=42

#2 train
def wprN((code,stop)):
	return code=='2' and 4<=stop<=12
def wprS((code,stop)):
	return code=='2' and 13<=stop<=22
def lenoxS((code,stop)):
	return code=='2' and 24<=stop<=27
def epkwyN((code,stop)):
	return code=='2' and 28<=stop<=39
def nostr((code,stop)):
	return code=='2' and 41<=stop<=47

#3 train
def lenoxN((code,stop)):
	return code=='3' and 1<=stop<=2
def epkwyS((code,stop)):
	return code=='2' and 48<=stop<=57

#4 train
def jerome((code,stop)):
	return code=='4' and 1<=stop<=15

#5 train
def dyre((code,stop)):
	return code=='5' and 1<=stop<=5

#6 train
def pelham((code,stop)):
	return code=='6' and 1<=stop<=19
def lex((code,stop)):
	if code=='6' and 21<=stop<=40: return True
	if code=='4' and 18<=stop<=23: return True
	return False

#7 train
def flushing((code,stop)):
	return code=='7'

#S Grand central
def gcs((code,stop)):
	return code=='9'

#A train
def eightN((code,stop)):
	return code=='A' and 2<=stop<=11
def eightM((code,stop)):
	if code=='A' and 12<=stop<=24: return True
	if code=='D' and stop==13: return True
	return False
def eightS((code,stop)):
	if code=='A' and 25<=stop<=34: return True
	if code=='D' and stop==20: return True
	return False
def fultonN((code,stop)):
	return code=='A' and 36<=stop<=40
def fultonM((code,stop)):
	return code=='A' and 43<=stop<=61
def fultonS((code,stop)):
	return code=='A' and 63<=stop<=65
def rockN((code,stop)):
	return code=='H' and 1<=stop<=4
def rockM((code,stop)):
	return code=='H' and 6<=stop<=11
def rockS((code,stop)):
	return code=='H' and 12<=stop<=15

#D train
def concourse((code,stop)):
	return code=='D' and 3<=stop<=12
def six((code,stop)):
	if code=='D' and 15<=stop<=21: return True
	if code=='A' and stop==32: return True
	return False
def fourN((code,stop)):
	return code=='R' and 31<=stop<=36
def west((code,stop)):
	if code=='B' and 12<=stop<=23: return True
	if code=='D' and stop==43: return True
	return False

#E train
def archer((code,stop)):
	return code=='G' and 5<=stop<=6
def queens((code,stop)):
	if code=='F' and 5<=stop<=7: return True
	if code=='G' and 8<=stop<=20: return True
	return False
def fiftythird((code,stop)):
	return code=='F' and 9<=stop<=12

#F train
def hill((code,stop)):
	return code=='F' and 1<=stop<=4
def sixtythird((code,stop)):
	return code=='B' and 4<=stop<=10
def les((code,stop)):
	return code=='F' and 14<=stop<=18
def culverN((code,stop)):
	return code=='F' and 20<=stop<=39
def culverS((code,stop)):
	return code=='D' and 42<=stop<=43

#G train
def cross((code,stop)):
	return code=='G' and 22<=stop<=36

#J train
def jamaicaN((code,stop)):
	return code=='J' and 12<=stop<=31
def jamaicaS((code,stop)):
	return code=='M' and 11<=stop<=23

#L train
def canarsie((code,stop)):
	return code=='L'

#M train
def myrtle((code,stop)):
	return code=='M' and 1<=stop<=10

#N train
def astoria((code,stop)):
	return code=='R' and 1<=stop<=8
def fiftyninth((code,stop)):
	return code=='R' and 11<=stop<=13
def bwy((code,stop)):
	return code=='R' and 14<=stop<=23
def fourM((code,stop)):
	return code=='R' and 39<=stop<=41
def sea((code,stop)):
	if code=='N' and 2<=stop<=10: return True
	if code=='D' and stop==43: return True
	return False

#Q train
def second((code,stop)):
	return code=='Q' and 3<=stop<=5



#Tests
#print(bwy7N(digestStopCode('112')))
#print(bwy7N(digestStopCode('101')))
#print(bwy7N(digestStopCode('119')))
#print(bwy7N(digestStopCode('120')))
#print(bwy7N(digestStopCode('A12')))
