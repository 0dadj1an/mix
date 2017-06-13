'''
def load(IP, MASK, NAME):
    if checkIPFormat(IP, MASK):
        
        session = cpauto.CoreClient('admin', '', '10.40.0.2')# vytvoreni nove session
          
        output = session.login()# login funkceprint 
    
        print output.status_code
        if str(output.status_code) == "200":
              
        
            finder = CheckPointFinder(session)# volani tridy Finder pro pouziti metod
            adder = CheckPointAdd(session)
            
            if str(MASK) != "32":            
    
                a = finder.findNetworkUIDs() # vola metody, ktera vraci vsechny UID siti jako slovnik
                check = False
                for item in a:
                     if finder.isNetworkExists(item, IP , MASK):
                         print "Network exists"
                         check = True
    
                if check == False:
                    print "Network does not exists, adding"
                    dic = {'subnet': IP,'mask-length': MASK, 'color': 'black'}
                    print dic
                    output = adder.addNetwork(NAME, dic)
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
        
        
    
    
        output = session.publish()
        print output.status_code
        
        output = session.logout()
        print output.status_code
        
    else:
        print "BAD IP and MASK format, leaving"
  '''
