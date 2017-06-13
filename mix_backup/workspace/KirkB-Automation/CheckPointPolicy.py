# -*- coding: utf-8 -*-

import cpauto
import sys
import csv 
import pprint
import time
from getpass import getpass

class Policy(object):
    def __init__(self, session):
        self.session = session
            
    # methods for finding all UID's of particulars objects
    def findPolicies(self):
        networks = cpauto.Policy(self.session)
        order = []
        output = networks.show_all(500, 0, order, 'uid')
        print output
        output_dictionary = output.json()
        helplist = output_dictionary['objects']
        print helplist