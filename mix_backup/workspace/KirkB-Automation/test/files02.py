'''
q = open("oujeeee.txt", "w")
q.write("test\n")
q.close()
print q


b = open("oujeeee.txt","a")
b.write("oujeeee\n")
b.write("oujeeee\n")
b.write("oujeeee\n")
b.write("oujeeee\n")
b.close()
'''


'''
with open("oujeeee.txt") as a_file:
  b =  a_file.read()
  print b.strip("\n") # removes new line character
  
'''
test = 'config.txt'
with open (test, 'w') as out:
    out.write('ahoj')
  

  

    
    
    






