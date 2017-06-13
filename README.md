# PersonalChina

This is a python script designed to run on the EdgeRouter X that creates and configures an outgoing whitelist firewall.
The goal of this project is to ensure that any software on my system can not phone home without my express approval.

Right now the only way to add rules is through the command line interface

    ruleUpdater.py action [args]

    actions:
            reload_all      create and reload all rules
            check_expired   check expired ips and refresh rules
            unlink_ruleset  unlink the rules, unblocks everything
            add_rule        add rule to a ruleset, requires -r, -i, and optional -t
            del_rule        delete rule from a ruleset, requires -r, and -i

    args:
            -r              rule list name, [src, dst]
            -i              ip x.x.x.x x.x.x.x/x or x.x.x.x-x.x.x.x
            -t              the number of seconds until this ip expires, ip does not expire if this is not included

Web interface is planned for the future