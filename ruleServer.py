#!/usr/bin/python

import BaseHTTPServer
import urllib
import os.path

SERVER_FILES = "serverFiles"

def parsePath(pathArgs):
	pathArgs = pathArgs.split("?")

	path = pathArgs[0][1:].split("/")
	args = pathArgs[1] if len(pathArgs) > 1 else ""

	path = [p for p in path if len(p) > 0]

	nArgs = {}
	for a in args.split("&"):
		argParts = a.split("=")

		if len(argParts[0]) == 0:
			continue
		
		key = urllib.unquote_plus(argParts[0])
		val = urllib.unquote_plus(argParts[1]) if len(argParts) > 1 else ''

		nArgs[key] = val
	
	args = nArgs

	return path, args

def readServerFile(file, staticVars = {}):
	
	if len(file) == 0:
		return False
	
	filePath = os.path.join(SERVER_FILES, file)

	if not os.path.isfile(filePath):
		return False

	ret = ""

	with open(filePath) as f:
		ret = f.read()

	for key in staticVars:
		replaceKey = "{$%s}" % key
		ret = ret.replace(replaceKey, staticVars[key])
	
	return ret

def run(server_class=BaseHTTPServer.HTTPServer, handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
	server_address = ('', 8000)
	httpd = server_class(server_address, handler_class)

	running = True
	while running:
		try:
			httpd.handle_request()
		except KeyboardInterrupt as e:
			running = False

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		# ret = ""

		# ret += str(self.client_address) + "\n"
		# ret += str(parsePath(self.path))

		# self.writeBody(body=ret)

		path, args = parsePath(self.path)
		path = map(lambda x: x.lower(), path)

		request = path[0] if len(path) > 0 else ""
		endpoint = path[1] if len(path) > 1 else ""

		if request == "file":
			staticVars = {}

			staticVars["clientIp"] = self.client_address[0]

			body = readServerFile(endpoint, staticVars)

			if body == False:
				self.writeBody(code=404, body="404 - not found")
			else:
				self.writeBody(body=body)
		else:
			self.writeBody(code=404, body="404 - not found")

		
	
	def writeBody(self, code=200, headers=[], mimeType="text/html; charset=utf-8", body=""):

		body = body.encode("utf_8")

		self.send_response(code)

		for h in headers:
			self.send_header(h[0], h[1])

		self.send_header("Content-type", mimeType)
		self.send_header("Content-length", len(body))

		self.end_headers()

		self.wfile.write(body)

run(handler_class=RequestHandler)