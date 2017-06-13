


import cpauto
    
session = cpauto.CoreClient('admin', 'cisco123', '192.168.0.250')
output = session.login()


output.status_code

networks = cpauto.Network(session)
output = networks.show_all()
print type(output)
print output

outputdictfromserver = output.json()
print type(outputdictfromserver)

print outputdictfromserver

helplist = outputdictfromserver['objects']
print helplist

finallistofnetworksuid = []

IP = ''
mask = ''

#find uid of subnet

count01 = 0
count02 = len(helplist)

while count01 < count02:
    str = helplist[count01]
    for ko in str:
       if ko == 'uid':
          a = str[ko]
          finallistofnetworksuid.append(a)
    count01 = count01 + 1
print finallistofnetworksuid


#find and print IP of subnet

for item in finallistofnetworksuid:
    a= finallistofnetworksuid.index("item")
    print type(a)
    '''
    str = finallistofnetworksuid[[finallistofnetworksuid].index("item")]
    print str
    output02 = networks.show(str)
    outputdictfromserver = output02.json()
    IP = outputdictfromserver['subnet4']
    mask = outputdictfromserver['mask-length4']
    print IP
    '''
#old way
'''

while count01 < count02:
    str = finallistofnetworksuid[count01]
    output02 = networks.show(str)
    outputdictfromserver = output02.json()
    #print outputdictfromserver
    IP = outputdictfromserver['subnet4']
    mask = outputdictfromserver['mask-length4']
    print IP
    print "{}/{}".format(IP, mask)
    count01 = count01 + 1
    IP2='172.16.10.0' 
           
    if (IP == IP2 and mask == mask):
         print "Nalezeno"
    else: 
        print "Nenalezeno"

    '''

    
    

        





