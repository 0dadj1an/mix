#
# discardSessions.py
# version 1.0
#
# The purpose of this script is to unlock objects, which were locked by another session of this user.
# The sessions will be unlocked by discarding changes which were done during that session.
# Only those sessions will be discarded which belong to the user and were created via Web APIs or CLI.
#
# written by: Check Point software technologies inc. 
# July 2016
#

# cp_management_api is a package that handles the communication with the Check Point management server.
from mgmt_api_lib import *

# A package for reading passwords without displaying them on the console.
import getpass
import sys

def main():
    with APIClient() as client:
    
        server   = raw_input("Enter server IP address or hostname: ")
        username = raw_input("Enter username: ")
        if sys.stdin.isatty():
            password = getpass.getpass("Enter password: ")
        else:
            print "Attention! Your password will be shown on the screen!"
            password = raw_input("Enter password: ")

	    # The API client, would look for the server's certificate SHA1 fingerprint in a file.
	    # If the fingerprint is not found on the file, it will ask the user if he accepts the server's fingerprint.
        # In case the user does not accept the fingerprint, exit the program.
        if client.check_fingerprint(server) is False:
            print "Could not get the server's fingerprint - Check connectivity with the server."
            exit(1)

        # login to server:
        login_res = client.login(server, username, password)
	
        if login_res.success is False:
            print "Login failed: {}".format(login_res.error_message)
            exit(1)
        
        showSessionsRes = client.api_query("show-sessions", "full")
        
        if not showSessionsRes.success:
            print "Failed to retrieve the sessions"
            return
        
        for sessionObj in showSessionsRes.data:
            # Ignore sessions that were not created with WEB APIs or CLI
            if sessionObj["application"] != "WEB_API":
                continue
            
            discardRes = client.api_call("discard", {"uid": sessionObj['uid']})
            if discardRes.success: 
                print "Session '{}' discarded successfully".format(sessionObj['uid'])
            else:
                print "Session '{}' failed to discard".format(sessionObj['uid'])
        
if __name__ == "__main__":
    main()
