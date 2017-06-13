#!/usr/bin/python

import os
import json

CFG_PATH = '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper'

RULESET_NAME = "personal_china"
DST_GROUP_NAME = "personal_china_dst_whitelist"
SRC_GROUP_NAME = "personal_china_src_whitelist"


def get_config_object(s_config):
    s_out = '{'
    i_current_indent = -1
    i_multiplyer = 4
    for s_line in s_config.splitlines():
        s_striped_line = s_line.strip(' ')
        i_spaces = len(s_line) - len(s_striped_line)
        i_loop_indent = i_spaces / i_multiplyer

        if i_loop_indent == i_current_indent and b_object_has_data:
            s_out += ','

        if s_striped_line[-1:] == '{':  # is object start
            b_object_has_data = False
            s_out += '"' + s_striped_line[:-2].strip('"') + '":{'

        elif s_striped_line[-1:] == '}':  # is object end
            b_object_has_data = True
            s_out += '}'

        else:  # is property#
            b_object_has_data = True
            tmp = s_striped_line.split(' ', 1)
            if len(tmp) == 1:
                tmp.append('"true"')
            s_out += '"' + tmp[0] + '":' + json.dumps(tmp[1].strip('"'))

        i_current_indent = i_loop_indent
    s_out += '}'

    return json.loads(s_out)

def begin():
    os.system("%s begin" % CFG_PATH)

def commit():
    os.system("%s commit" % CFG_PATH)
    os.system("%s end" % CFG_PATH)

def update_group(name, addressList = []):

    os.system("%s delete firewall group address-group %s" % (CFG_PATH, name))

    os.system("%s set firewall group address-group %s" % (CFG_PATH, name))

    for address in addressList:
        os.system("%s set firewall group address-group %s address %s" % (CFG_PATH, name, address))

def create_ruleset():

    fwName = "%s set firewall name %s" % (CFG_PATH, RULESET_NAME)

    os.system("%s delete firewall name %s" % (CFG_PATH, RULESET_NAME))

    os.system("%s default-action reject" % fwName)

    os.system("%s rule 10 state established enable" % fwName)
    os.system("%s rule 10 state related enable" % fwName)
    os.system("%s rule 10 description \"Allow established connections\"" % fwName)
    os.system("%s rule 10 action accept" % fwName)

    os.system("%s rule 20 protocol tcp_udp" % fwName)
    os.system("%s rule 20 destination port 53" % fwName)
    os.system("%s rule 20 description \"Allow DNS\"" % fwName)
    os.system("%s rule 20 action accept" % fwName)

    os.system("%s rule 30 source group address-group %s" % (fwName, SRC_GROUP_NAME))
    os.system("%s rule 30 description \"Allow src whitelist\"" % fwName)
    os.system("%s rule 30 action accept" % fwName)

    os.system("%s rule 40 destination group address-group %s" % (fwName, DST_GROUP_NAME))
    os.system("%s rule 40 description \"Allow dst whitelist\"" % fwName)
    os.system("%s rule 40 action accept" % fwName)
    
    os.system("%s set interfaces ethernet eth0 firewall out name %s" % (CFG_PATH, RULESET_NAME))

def remove_ruleset():
    os.system("%s delete interfaces ethernet eth0 firewall out name %s" % (CFG_PATH, RULESET_NAME))

def refresh():
    update_group(DST_GROUP_NAME)
    update_group(SRC_GROUP_NAME)
    create_ruleset()

# f_handle = os.popen(CFG_PATH + ' show firewall')
# s_config = f_handle.read()
# o_config = get_config_object(s_config)
# print(json.dumps(o_config))


# update_group(DST_GROUP_NAME)
# update_group(SRC_GROUP_NAME, ["192.168.1.10"])
# create_ruleset()
# remove_ruleset()