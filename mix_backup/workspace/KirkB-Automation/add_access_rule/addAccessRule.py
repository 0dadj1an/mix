#
# addAccessRule.py
# version 1.0
#
#
# This example demonstrates communication with Check Point Management server using Management API Library in Python.
# The demonstrated commands are:
#
#   1. login
#   2. adding an access rule to the top of Network layer
#   3. publishing the changes
#
# Logout command is called automatically after the work with Management API Library is completed.
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

        ruleName = raw_input("Enter the name of the access rule: ")

	    #
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
        
        # add a rule to the top of the "Network" layer
        addRuleResponse = client.api_call("add-access-rule", {"name": ruleName, "layer" : "Network", "position" : 
                                                "top"});
        
        if addRuleResponse.success:
            
            print "The rule: '{}' has been added successfully".format(ruleName)
            
            # publish the result
            publishRes = client.api_call("publish", {});
            if publishRes.success:
                print "The changes were published successfully."
            else:
                print "Failed to publish the changes."
        else:
            print "Failed to add the access-rule: '{}', Error: {}".format(ruleName, addRuleResponse.error_message)
            
if __name__ == "__main__":
    main()
