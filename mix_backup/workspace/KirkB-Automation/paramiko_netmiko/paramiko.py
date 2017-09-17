import paramiko
import time



ip = '184.105.247.70'
username = 'pyclass'
password = '88newclass'

remote_conn=paramiko.SSHClient()
# avoid issues with not trusted targets
remote_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())

remote_conn.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)

remote_conn02 = remote_conn.invoke_shell()

output = remote_conn02.recv(1000)

print output

remote_conn02.send("conf t\n")

output = remote_conn02.recv(5000)

print output









