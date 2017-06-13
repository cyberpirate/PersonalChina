#!/usr/bin/python

import sqlite3
import os.path
import time

DB_NAME = "whitelists.db"

def load_database():
	
	conn = None

	if not os.path.isfile(DB_NAME):
		conn = sqlite3.connect(DB_NAME)

		conn.cursor().execute('create table `list` (listName text, ip text, expireTime integer)')
	
	else:
		conn = sqlite3.connect(DB_NAME)

	return conn

def clear_expired(conn):
	c = conn.cursor()

	numDeleted = 0
	for n in c.execute("select count(*) from `list` where expireTime != 0 and expireTime < ?", (int(time.time()), )):
		numDeleted = n[0]

	c.execute("delete from `list` where expireTime != 0 and expireTime < ?", (int(time.time()), ))

	return numDeleted > 0

def get_lists(conn):
	lists = {}

	for listName, ip in conn.cursor().execute("select listName, ip from `list`"):

		if listName not in lists:
			lists[listName] = []
		
		lists[listName].append(ip)
	
	return lists

def add(conn, ruleName, ip, expireTime = 0):
	conn.cursor().execute("insert into `list` (listName, ip, expireTime) values (?, ?, ?)", (ruleName, ip, expireTime))

def remove(conn, ruleName, ip):
	conn.cursor().execute("delete from `list` where ruleName = ? and ip = ?", (ruleName, ip))

# db = load_database()

# # add(db, "r1", "0.0.0.0", 0)
# # add(db, "r1", "0.0.0.1", 0)
# # add(db, "r1", "0.0.0.2", 0)
# # add(db, "r1", "0.0.0.3", 0)
# # add(db, "r1", "0.0.0.4", 0)

# # add(db, "r2", "0.0.0.0", 10)
# # add(db, "r2", "1.0.0.0", 10)
# # add(db, "r2", "2.0.0.0", 10)
# # add(db, "r2", "3.0.0.0", 10)
# # add(db, "r2", "4.0.0.0", 10)

# # add(db, "r3", "0.0.0.0", int(time.time()) + 60*60)
# # add(db, "r3", "0.1.0.0", int(time.time()) + 60*60)
# # add(db, "r3", "0.2.0.0", int(time.time()) + 60*60)
# # add(db, "r3", "0.3.0.0", int(time.time()) + 60*60)
# # add(db, "r3", "0.4.0.0", int(time.time()) + 60*60)

# # print clear_expired(db)
# lists = get_lists(db)
# print(lists)

# db.commit()
# db.close()