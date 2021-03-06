import telnetlib
import time
import socket
import sys


TIMEOUT = 6
TELNET_PORT = 23

class ConnectDevice02(object):
    
    
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        try:
            self.connection = telnetlib.Telnet(self.ip, TELNET_PORT, TIMEOUT)
        except socket.timeout:
                sys.exit("Unable to connect due timeout")
        self.telnetLogin()
        
    def telnetSend(self, command):
        
         command = command.rstrip()
         self.connection.write(command + '\n')
         time.sleep(1)
         return self.connection.read_very_eager()


    def telnetLogin(self):
         output = self.connection.read_until("sername:", TIMEOUT)
         self.connection.write(self.username +'\n')
         output = output + self.connection.read_until("ssword:", TIMEOUT)
         self.connection.write(self.password +'\n')
         return output
     
    def telnetClose():
         self.connection.close()


            
def main():
    
    ip_add = raw_input("write IP" + '\n')
    username = raw_input("write username" + '\n')
    password = raw_input("write password" + '\n')
    
    new_connection = ConnectDevice02(ip_add, username, password)
    new_connection.telnetSend('terminal length 0')
    new_connection.telnetSend('show version')
    
    new_connection.telnetClose()
    
    

        
        