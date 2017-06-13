#!/usr/bin/python

from fileSemaphore import fSem as lock
import ruleManager
import ruleCacher
import sys
import time

DB_LOCK = "db.lock"

def load_db_lists():
	db = ruleCacher.load_database()

	expirations = ruleCacher.clear_expired(db)
	lists = ruleCacher.get_lists(db)

	db.commit()
	db.close()

	return (lists, expirations)

def update_rules(lists):

	srcList = []
	dstList = []

	if ruleManager.SRC_GROUP_NAME in lists:
		srcList = lists[ruleManager.SRC_GROUP_NAME]
	if ruleManager.DST_GROUP_NAME in lists:
		dstList = lists[ruleManager.DST_GROUP_NAME]

	ruleManager.begin()
	ruleManager.refresh()

	ruleManager.update_group(ruleManager.SRC_GROUP_NAME, srcList)
	ruleManager.update_group(ruleManager.DST_GROUP_NAME, dstList)
	ruleManager.commit()

def reload_all():
	with lock(DB_LOCK):
		lists, expirations = load_db_lists()

		update_rules(lists)

def check_expired():
	with lock(DB_LOCK):
		lists, expirations = load_db_lists()

		if expirations:
			return

		update_rules(lists)

def unlink_ruleset():
	ruleManager.begin()
	ruleManager.remove_ruleset()
	ruleManager.commit()

def add_rule(ruleName, ip, expireTime = 0):
	with lock(DB_LOCK):
		db = ruleCacher.load_database()

		ruleCacher.add(db, ruleName, ip, expireTime)
		
		ruleCacher.clear_expired(db)
		lists = ruleCacher.get_lists(db)

		db.commit()
		db.close()

		update_rules(lists)

def del_rule(ruleName, ip):
	with lock(DB_LOCK):
		db = ruleCacher.load_database()

		ruleCacher.remove(db, ruleName, ip)
		
		ruleCacher.clear_expired(db)
		lists = ruleCacher.get_lists(db)

		db.commit()
		db.close()

		update_rules(lists)

def cli_help():
	print("ruleUpdater.py action [args]\n")
	print("actions:")
	print("\treload_all\tcreate and reload all rules")
	print("\tcheck_expired\tcheck expired ips and refresh rules")
	print("\tunlink_ruleset\tunlink the rules, unblocks everything")
	print("\tadd_rule\tadd rule to a ruleset, requires -r, -i, and optional -t")
	print("\tdel_rule\tdelete rule from a ruleset, requires -r, and -i")
	print("\nargs:")
	print("\t-r\t\trule list name, [src, dst]")
	print("\t-i\t\tip x.x.x.x x.x.x.x/x or x.x.x.x-x.x.x.x")
	print("\t-t\t\tthe number of seconds until this ip expires, ip does not expire if this is not included")

def cli_exit():
	cli_help()
	exit()

if __name__ == "__main__":
	# cli_help()

	action = sys.argv[1] if len(sys.argv) > 1 else ""
	argKeys = sys.argv[2::2] if len(sys.argv) > 2 else []
	argValues = sys.argv[3::2] if len(sys.argv) > 3 else []

	if len(action) == 0 or len(argKeys) != len(argValues):
		cli_exit()

	if action == "reload_all":
		reload_all()

	elif action == "check_expired":
		check_expired()

	elif action == "unlink_ruleset":
		unlink_ruleset()

	else:
		ruleName = ""
		ip = ""
		expireTime = 0

		for i in range(len(argKeys)):
			key = argKeys[i]
			value = argValues[i]

			if key == "-r":
				if value == "src":
					ruleName = ruleManager.SRC_GROUP_NAME
				elif value == "dst":
					ruleName = ruleManager.DST_GROUP_NAME
				else:
					cli_exit()
			
			elif key == "-i":
				ip = value
			
			elif key == "-t":
				expireTime = int(time.time()) + int(value)
			
			else:
				cli_exit()

		if action == "add_rule":
			if len(ruleName) == 0 or len(ip) == 0:
				cli_exit()

			add_rule(ruleName, ip, expireTime)

		elif action == "del_rule":
			if len(ruleName) == 0 or len(ip) == 0:
				cli_exit()

			del_rule(ruleName, ip)

		else:
			cli_exit()
