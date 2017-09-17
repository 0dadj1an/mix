# -*- coding: utf-8 -*-

import cpauto
import sys
import csv 
import pprint
import time
from getpass import getpass



class CheckPointFinder(object):
    def __init__(self, session):
        self.session = session
            
    # methods for finding all UID's of particulars objects
    def findNetworkUIDs(self):
        networks = cpauto.Network(self.session)
        order = []
        output = networks.show_all(500, 0, order, 'uid')
        output_dictionary = output.json()
        helplist = output_dictionary['objects']
        return helplist
    
    def findHostUIDs(self):
        hosts = cpauto.Host(self.session)
        order = []
        output = hosts.show_all(500, 0, order, 'uid')
        output_dictionary = output.json()
        helplist = output_dictionary['objects']
        return helplist
    
    def findPolicyPackagesUIDs(self):
        packages = cpauto.PolicyPackage(self.session)
        order = []
        output = packages.show_all(500, 0, order, 'uid')
        output_dictionary = output.json()
        helplist = output_dictionary['packages']
        return helplist
    def findLayers(self):
        return True
        
        
        
        
    #methods for finding concrete UID.
    def isNetworkExists(self, uid, ip, mask):
            network = cpauto.Network(self.session)
            output = network.show(uid)
            print output
            outputdictfromserver = output.json()
            print outputdictfromserver
            IP = outputdictfromserver['subnet4'] 
            MASK = outputdictfromserver['mask-length4']
            #print "object: {} {}".format(IP, MASK)
            if (str(IP) == ip and str(MASK) == mask):
                 return True
            else: 
                 return False
             
    def isHostExist(self, uid, ip):
            host = cpauto.Host(self.session)
            output = host.show(uid)
            outputdictfromserver = output.json()
            #print outputdictfromserver
            
            IP = outputdictfromserver['ipv4-address'] 
            #print IP
            if (str(IP) == ip):
                 return True
            #
            else: 
                 return False        
    def isPolicExists(self, uid):
        package = cpauto.PolicyPackage(self.session)
        output = package.show(uid)
        outputdictfromserver = output.json()
        #pprint.pprint(outputdictfromserver)
        return outputdictfromserver
        
    def policyName(self, list):
         for items in list:
             return item
        
        
        
class CheckPointAdd(object):
    
    def __init__(self, session):
        self.session = session
            
    def addHost(self, name, IP, dic):
        host = cpauto.Host(self.session)
        output = host.add(name, IP, ipv4_address='', ipv6_address='' , params=dic)
        print output.json()
        #print >>log.txt, output.json()
        return output.status_code 
    
    def addNetwork(self, name, dic):
        network = cpauto.Network(self.session)
        output = network.add(name, params=dic)
        print output.json()
        #print >>log.txt, output.json()
        return output.status_code   

    

def checkIPFormat(ip_add, mask):
    
    '''
    testing function if IP address entered into cmd is correct(all octetcs and only numbers)
    '''
    checker = 1
    
    ip4_sections = ip_add.split(".")
    mask_sections = mask.split(".")
    #print len(ip4_sections)
    #print len(mask_sections)
    if len(ip4_sections) == 4 and (len(mask_sections) == 4 or len(mask_sections) == 1):
        for item in ip4_sections:
            if item.isdigit() == False:
                checker = 0
        for item in mask_sections:
            if item.isdigit() == False:
                checker = 0        
    else:
        #print "Bad IP format, try it again"
        checker = 0           
                
    if checker == 1:
        print"TRUE"
        return  True
       
    else:
         #print "Bad IP format, try it again"
         print "FALSE"
         return False 


def csvLoad(path):
    reader = csv.DictReader(open(path, 'rb'))
    dic_list = []

    for line in reader:
         dic_list.append(line)
    

    #pprint.pprint(dic_list)
    return dic_list
    
      
def constructNetName(dic):
    
    stringCommon = 'net_'
    stringComa = '_'
    stringBackSlash = '/'
    stringCategory = dic['Network category']
    stringVlan = dic['VLAN']
    stringLocalita = dic['Location']
    stringIP = dic['Network']
    stringMask = dic['Mask length']
    stringFull = (stringCommon + stringCategory + stringComa + stringVlan + stringComa + stringLocalita + stringComa + stringIP + 
                 stringComa + stringMask)
    return stringFull    

def constructHostName(dic):
    
    stringCommon = 'net_'
    stringComa = '_'
    stringBackSlash = '/'
    stringCategory = dic['Network category']
    stringVlan = dic['VLAN']
    stringLocalita = dic['Location']
    stringIP = dic['Network']
    stringMask = dic['Mask length']
    stringFull = (stringCommon + stringCategory + stringComa + stringVlan + stringComa + stringLocalita + stringComa + stringIP + 
                 stringComa + stringMask)
    return stringFull 

def showPolicy():
    
    session = cpauto.CoreClient('admin', 'checkpoint123', '10.120.1.111')# vytvoreni nove session
    output = session.login()# login funkceprint 
    
    print output.status_code
    if str(output.status_code) == "200": # if status is okay, then continue  
        finder = CheckPointFinder(session)
        list_a = finder.findPolicyPackagesUIDs()
        for item in list_a:
            print "###################"
            output = finder.isPolicExists(item)
            print type(output)
            stringA = output['name']
            print stringA
            print "###################"
            
        

        output = session.publish()
        if str(output.status_code) != "200":
            print "Cannot publish"
            print output.status_code
            print output.json()
        else:
            print "Published"
        
        output = session.logout()
        if str(output.status_code) != "200":
            print "Cannot logout "
            print output.status_code
            print output.json()
        else:
            print "Logout"
    else:
        print "Can not connect to API"
        output = session.logout()
        sys.exit()
        
        
        
def loadObjects():
    ##create session to API   
    #password = getpass()
    session = cpauto.CoreClient('admin', 'checkpoint123', '10.120.1.111')# vytvoreni nove session
    output = session.login()# login funkceprint 
    
    print output.status_code
    print output.json()
    if str(output.status_code) == "200": # if status is okay, then continue  
         
         finder = CheckPointFinder(session)# volani tridy Finder pro pouziti metod
       
         adder = CheckPointAdd(session)
         
         try:
            
            object_list = csvLoad('test01.csv')
            print object_list
         except IOError:
             print "bad csv file path"
             output = session.logout()
             print output.status_code
             sys.exit()
             
         try:
             
             for item in object_list:
                 print item
                 IP = getIP(item)  
                 print IP
                 MASK = getMask(item)
                 print MASK
                 COMMENT = getDescription(item)
                 print COMMENT
                
                 #print MASK
                 if checkIPFormat(IP, MASK):
                     NAME = constructNetName(item)
                     print NAME
                     print MASK
                     if str(MASK) != "32":            
                        
                        a = finder.findNetworkUIDs() # vola metody, ktera vraci vsechny UID siti jako slovnik
                        check = False
                        print a
                        for item in a:
                             print item
                             if finder.isNetworkExists(item, IP , MASK):
                                 print"TEST_IN"
                                 print  "Network exists: {} {}".format(IP, MASK)
                                 check = True
                                 break
            
                        if check == False:
                            print "Network does not exists, adding"
                            dic = {'subnet': IP,'mask-length': MASK, 'color': 'black', 'comments': COMMENT}
                            #print dic
                            output = adder.addNetwork(NAME, dic)
                            time.sleep(1)
                         #print output
                            if str(output) == "500":
                                print "host can not be added, same name probably"
                     
                     else: 
                         #adder = CheckPoint
                
                         b = finder.findHostUIDs()
                         check = False
                         for item in b:
                             if finder.isHostExist(item, IP):
                                 print "host exists"
                                 check = True
            
                         if check == False:
                             print "host does not exists, adding"
                             dic = {'color': 'black'}
                             print dic
                             output = adder.addHost(NAME, IP, dic)
                         #print output
                             if str(output) == "500":
                                 print "host can not be added, same name probably"
                 else:
                     print "BAD IP and MASK format in csv, fix it:"
                     pprint.pprint(item)
                     print "#################"
                  
                    
                    
                    
         except KeyError:
             print "Key handling in dictionary is bad, non existing parameter etc., check your cvs or parameters in it"
             print "publishing previous changes"
        
            
             
             
             
    else:
        print "Can not connect to API"
        list = output.json()
        print list['message']
        sys.exit()
    
    
    
    output = session.publish()
    if str(output.status_code) != "200":
        print "Cannot publish"
        print output.status_code
        print output.json()
    else:
        print "Published"
        
    output = session.logout()
    if str(output.status_code) != "200":
        print "Cannot logout "
        print output.status_code
        print output.json()
    else:
        print "Logout"
    

def getIP(dic):
    
    return dic['Network']

def getMask(dic):
    
    return dic['Mask length']

def getDescription(dic):
    
    return dic['Name']

def testFWinterface(dic):
    return True
    
    
def main():
        
    loadObjects()
    #print "uncomment loadObject method"
    #showPolicy()
if __name__ == "__main__":
    main()