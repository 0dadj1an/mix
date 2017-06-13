from snmp_helper import snmp_get_oid,snmp_extract

COMMUNITY_STRING = 'TEST'
SNMP_PORT = 161
a_device = ('192.168.0.250', COMMUNITY_STRING, SNMP_PORT)

snmp_data = snmp_get_oid(a_device, oid='1.3.6.1.2.1.1.3.0', display_errors=True)
snmp_data
output = snmp_extract(snmp_data)
print output
