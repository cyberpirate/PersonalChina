# import re

# byteReg = "(2([0-4][0-9]|5[0-5])|[01]?[0-9][0-9]|[0-9])"
# ipReg = "(%s\\.){3}%s" % (byteReg, byteReg)
# rangeReg = ipReg + "(\\/([0-9]|[12][0-9]|3[0-6]))"
# ipToIpReg = ipReg + "-" + ipReg

# ipReg = re.compile("^" + ipReg + "$")
# rangeReg = re.compile("^" + rangeReg + "$")
# ipToIpReg = re.compile("^" + ipToIpReg + "$")

# print(ipReg.match("98.131.185.136").group())
# print(rangeReg.match("5.101.218.0/24").group())
# print(ipToIpReg.match("98.131.185.136-98.131.185.136").group())

import os

CFG_PATH = '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper'

os.system("%s show dns forwarding statistics" % CFG_PATH)