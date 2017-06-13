import cpauto
    
session = cpauto.CoreClient('admin', 'cisco123', '192.168.0.250')
output = session.login()

policies = cpauto.PolicyPackage(session)

output = policies.show_all()
outputdictfromserver = output.json()

outputdictfromserver['packages']

counter=0

print outputdictfromserver
output = session.logout()
print output.status_code  
                  
