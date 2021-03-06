import time
import paramiko



def disable_paging(connection):
    '''disable paging by entering terminal lenght'''
    connection.send("terminal length 0\n")
    time.sleep(1)
    output = connection.recv(1000)
    return output

def showVersion(connection):
    ''' method for showing the version '''
    connection.send("show version\n")
    time.sleep(1)
    output = connection.recv(5000)
    return output

def enterConfig(connection):
    '''congig mode method '''
    connection.send("conf t\n")
    time.sleep(1)
    output = connection.recv(5000)
    return output

def loginBuffered(connection):
    ''' changing login buffer '''
    connection.send("loggin buffered 65000\n")
    time.sleep(1)
    output = connection.recv(5000)
    return output

def showIPbrief():
    print


def main():
    
     ip = '184.105.247.70'
     username = 'pyclass'
     password = ''
     
     remote_conn=paramiko.SSHClient()
    # avoid issues with not trusted targets
     remote_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
     remote_conn.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)
     remote_conn02 = remote_conn.invoke_shell()
     disable_paging(remote_conn02)
     enterConfig(remote_conn02)
     output = loginBuffered(remote_conn02)
     
     print output

    
if __name__ == "__main__":
    main()
