import re # importing regular expression package


with open("cdp.txt") as file: #open a file
    for line in file: # goes through lines
        a = re.search(r"  IP address: (.+).", line) #looking for expression starting by   IP address: pattern for each line, return position, not actual data (. means any character, + means more times)
        if a: # checking if pattern was found
           print type(a)
           print a.group(1) # print everything behind pattern on position 1
           
        else:
            continue
'''

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

    

