import telnetlib
import time
import socket
import sys



TIMEOUT = 6
TELNET_PORT = 23





def telnetSend(connection, command):
    command = command.rstrip()
    connection.write(command + '\n')
    time.sleep(1)
    return connection.read_very_eager()


def telnetLogin(connection, username, password):
    output = connection.read_until("sername:", TIMEOUT)
    connection.write(username +'\n')
    output = output + connection.read_until("ssword:", TIMEOUT)
    connection.write(password +'\n')
    return output

def telnetConnection(ip_add):
     try:
        return telnetlib.Telnet(ip_add, TELNET_PORT, TIMEOUT)
     except socket.timeout:
        sys.exit("Unable to connect due timeout")
        
    
    

def main():
    ip_add = raw_input("write IP" + '\n')
    username = raw_input("write username" + '\n')
    password = raw_input("write password" + '\n')
   
        
    connection = telnetConnection(ip_add)    
    output = telnetlogin(connection, username, password)
   
    time.sleep(1)
    
    output = connection.read_very_eager()
    output = telnetSend(connection, 'terminal length 0')
    output = telnetSend(connection, 'show version')
    print output
    
    connection.close()
    
if __name__ == "__main__":
    main()
    
    
        