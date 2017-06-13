#!/usr/bin/python

# Created By James B. Anderson
# Last Modified: 03/19/2017
# This scripts gets the `Emerging Threats` blacklist and adds the
# IP ranges into an object group that can be used with WAN interface
# firewall rules. Feel free to use this and modifiy it!
# 
# Thanks to m-hume on github.com for the 'get_config_object' function.

import sys
import getopt
import json
import os
import subprocess
import re

CFG_PATH = '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper'
CWD = os.getcwd()
IP_STRING = re.compile(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\/\d{1,2}')
blacklist_ips = []


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


def remove_blacklist():
    ''' Remove the blacklist when done '''
    subprocess.check_call([
        "rm",
        CWD + "/emerging-Block-IPs.txt"])


def get_blacklist():
    ''' Use `wget` to download the IP list to the router '''
    subprocess.call(["wget",
                     "http://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt",
                     CWD])


def add_range_to_list(ip_range):
    ''' Check for duplicates, add to list if not found '''
    if blacklist_ips.count(ip_range) <= 0:
        blacklist_ips.append(ip_range)


def check_for_ip(line):
    ''' Check the line string for an IP address '''
    found = IP_STRING.search(line)
    if found:
        add_range_to_list(found.group(0))


def create_firewall_group(group_name):
    ''' Create the blacklist firewall group w/IP addresses'''
    os.system(CFG_PATH + " begin")
    print("Entered configuration mode...")
    print("Adding firewall group {0}...".format(group_name))
    os.system(CFG_PATH + " set firewall group address-group {0} "
              "description 'Blacklist IP Address Group'".format(group_name))
    print("Added firewall group {0}...".format(group_name))
    print("Adding IP ranges from blacklist...")
    for bl_ip in blacklist_ips:
        os.system(CFG_PATH + " set firewall group address-group {0} "
                  "address {1}".format(group_name, bl_ip))
    print("Done adding blacklist IP ranges...")
    print("Commiting and saving changes...")
    os.system(CFG_PATH + " commit")
    os.system(CFG_PATH + " end")
    print("Done creating firewall group...")


def update_group(group_name):
    ''' Update the firewall group with the new list '''
    os.system(CFG_PATH + " begin")
    print("Entered configuration mode...")
    print("Removing old IP ranges...")
    os.system(
        CFG_PATH + " delete firewall group address-group {0} address".format(group_name))
    os.system(CFG_PATH + " commit")
    os.system(CFG_PATH + " end")
    print("Old IP ranges removed...")
    os.system(CFG_PATH + " begin")
    print("Adding new IP ranges to object group...")
    for bl_ip in blacklist_ips:
        os.system(CFG_PATH + " set firewall group address-group {0} "
                  "address {1}".format(group_name, bl_ip))
    os.system(CFG_PATH + " commit")
    os.system(CFG_PATH + " end")
    print("Done updating the firewall group.")


def main(argv):
    ''' Main function to get cli arguments and process data '''
    help_msg = ("\nUsage: blacklist.py -n <networkgroup>\n")
    net_grp_name = ''
    group_found = False

    try:
        opts, args = getopt.getopt(
            argv, "hn:", ["networkgroup="])
    except getopt.GetoptError:
        print(help_msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == ('-h', '--help'):
            print(help_msg)
            sys.exit(1)
        elif opt in ("-n", "--networkgroup"):
            net_grp_name = arg

    get_blacklist()
    with open('emerging-Block-IPs.txt', 'r') as file:
        for line in file:
            check_for_ip(line)
    remove_blacklist()
    f_handle = os.popen(CFG_PATH + ' show firewall')
    s_config = f_handle.read()
    o_config = get_config_object(s_config)

    try:
        for group in o_config['group']:
            if group == "address-group {}".format(net_grp_name):
                group_found = True
    except KeyError:
        print("No firewall groups found on router!"
              "Creating firewall address group {0} on router...\n".format(net_grp_name))
        create_firewall_group(net_grp_name)
        sys.exit(1)

    if group_found is False:
        print("Creating firewall address group {0} on router...\n".format(
            net_grp_name))
        create_firewall_group(net_grp_name)
        sys.exit(0)
    else:
        print("Firewall group already exists. Updating group...")
        update_group(net_grp_name)
        sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
