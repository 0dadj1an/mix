
'''
def create_network_device(ip, username, password):
    net_device = {}
    net_device['ip'] = ip
    net_device['username'] = username
    net_device['password'] = password
    
    return net_device

rtr1 = create_network_device('10.1.1.1', 'ivos', 'ivos')
print rtr1
'''

class NetDevice(object):
    
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        



rtr1=NetDevice('10.1.1.1', 'ivos', 'ivos')


        
  



    
    