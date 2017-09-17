import re # importing regular expression package
import csv

with open('test01.csv') as csvfile:
     rule = {}
     reader=csv.DictReader(csvfile)   
     for row in reader:
            if ';' in row['source']:
                rule['source']=row['source'].split(';')
                print rule['source']
            
            else:
                rule['source']=row['source']
            #destination
            if ';' in row['destination']:
                rule['destination']=row['destination'].split(';')
                for item in rule['destination']:
                    if re.search(r"host:(.+).", item):
                      print "jsem host"
                      print item
            else:
                rule['destination']=row['destination']
            #service
            if ';' in row['service']:
                rule['service']=row['service'].split(';')
            else:
                rule['service']=row['service']
            #non multi-value fields
            rule['action']=row['action']
            rule['track']=row['track']
            rule['name']=row['name']
           
         

