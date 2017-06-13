
x=10
y=20
z=30


def namespace01():        
    
  def namespace02():
          x=0.5
          
          print x
          print y 
          print z  
  x=1
  y=2
  
  print x
  print y
  print z
  namespace02()
     
    
namespace01()
print x
print y 
print z 

