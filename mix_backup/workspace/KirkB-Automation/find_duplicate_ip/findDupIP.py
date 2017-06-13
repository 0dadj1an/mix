#
# findDupIP.py
# version 1.0
#
#
# Look for duplicate IP addresses in all the host objects.
# written by: Check Point software technologies inc. 
# December 2015
#


# cp_management_api is a package that handles the communication with the Check Point management server.
from mgmt_api_lib import *

# A package for reading passwords without displaying them on the console.
import getpass
import sys


def main():
    with APIClient() as client:
    
        # create debug file. The debug file will hold all the communication between the python script and Check Point's management server.
        client.debug_file = "api_calls.json"
    
        server = raw_input("Enter server IP address or hostname:")
        username = raw_input("Enter username: ")
        if sys.stdin.isatty():
            password = getpass.getpass("Enter password: ")
        else:
            print "Attention! Your password will be shown on the screen!"
            password = raw_input("Enter password: ")

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

        # show hosts
        show_hosts_res = client.api_query("show-hosts", "full")
        if show_hosts_res.success is False:
            print "Failed to get the list of all host objects: {}".format(show_hosts_res.error_message)
            exit(1)

	# obj_dictionary - for a given IP address, get an array of hosts (name, unique-ID) that use this IP address.
    obj_dictionary = {}
	
	# DupIPSet - a collection of the duplicate IP addresses in all the host objects.
    DupIPSet = set()
	
    for host in show_hosts_res.data:
        ipaddr = host["ipv4-address"]
        host_data = {"name" : host["name"], "uid" : host["uid"]}
        if ipaddr in obj_dictionary:
            DupIPSet.add(ipaddr)
            obj_dictionary[ipaddr] += [host_data] ## '+=' modifies the list in place
        else:
            obj_dictionary[ipaddr] = [host_data]

    # print list of duplicate IP addresses to the console
    print("\n")
    print ("List of Duplicate IP addresses: ")
    print ("------------------------------- \n")

    if len(DupIPSet) == 0:
        print "No hosts with duplicate IP addresses"

    # for every duplicate ip - print hosts with that ip:
    for dup_ip in DupIPSet:
        print ("\nIP Address: " + dup_ip + "")
        print ("----------------------------------")

        for obj in obj_dictionary[dup_ip]:
            print (obj["name"] + " (" + obj["uid"] + ")")

if __name__ == "__main__":
    main()
