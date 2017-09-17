import re # importing regular expression package
import csv


## napln list slovnikama z csvcka
list =[] # list
a=0 # pocitadlo
with open('app_hosts_withregex', 'rb') as csvfile:
        reader=csv.DictReader(csvfile)
      
        for row in reader:
            a = a+1
            row ['host'] = '.*\.'+row['host']+"\.*"
            list.append(row)
            
            
print "###"

keys = list[0].keys()
with open('app_hosts_withregex_changed', 'wb') as csvfile:
    dict_writer = csv.DictWriter(csvfile, keys)
    dict_writer.writeheader()
    dict_writer.writerows(list)    
    
with open('app_hosts_withregex_changed', 'rb') as csvfile:
        reader=csv.DictReader(csvfile)
      
        for row in reader:
            print row ['host']

            
        
            

           
            
          
'''

a = re.search(r"  IP address: (.+).", line)
           #looking for expression starting by   IP address: pattern for each line, return position, not actual data (. means any character, + means more times)
          if a: # checking if pattern was found
              print type(a)
              print a.group(1) # print everything behind pattern on position 1
           
          else:
               continue
               
f = open("cdp.txt")
cdp_data = f.read()
#print re.findall(r"IP address: .+",  cdp_data)
#print re.findall(r"IP address: (.+)",  cdp_data)
z= re.findall(r"Platform: (.+?) (.+?),  Capabilities: (.+)",  cdp_data)
print z


for vendor,model,type in z:
    print vendor
    print model
    print type


'''     

    


