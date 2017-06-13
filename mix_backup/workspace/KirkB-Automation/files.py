'''
readlines() - getting back list of all lines
seek(0) - getting back to the start of line
readline() --getting back line by line
read() -getting back whole bunch of text 
'''

f = open("cdp.txt", "r")
a = f.readlines()
print a

print "##############"
print''

q = open("cdp.txt", "r")
b = q.read()
print b

print "##############"

f.seek(0)

for line in f:
    print line
    
print "##############"

f.seek(0)
for line in f:
    print line.strip("\n")
    
print "##############"



