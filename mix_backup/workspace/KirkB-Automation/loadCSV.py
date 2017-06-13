
# -*- coding: utf-8 -*-


import csv 
import pprint
import json




reader = csv.DictReader(open('test01.csv', 'rb'))
dic_list = []
print 'net_cat_vlan_IP_mask_Location'
print '################################'
for line in reader:
    dic_list.append(line)

for item in dic_list:
   
     print 'net_' + item['Network category'] + '_' + item['VLAN'] + '_' +  item['Location'] + '_' + item['Network'] + '_' + item['Mask length'] + "#####" + item['Name']
     
     


