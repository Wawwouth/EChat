import websocket
import select
import json
import thread
import time
import sys
from urllib import *

# Avoid creating .pyc files
sys.dont_write_bytecode = True

host = "95.142.101.119"
port = 12565
uid = "97723"
salt = "esyznje1y0usos44ockcock80ssks04cc"
join_data = json.dumps({"roomID":23, "userID":uid, "salt":salt})

class SocketIO():
	def __init__(self, host, port):
		self.PORT = port
		self.HOST = host
		self.event_handler = {}
		self.connect()
 
	def __del__(self):
		self.close()
 
	def handshake(self,host,port):
		u = urlopen("http://%s:%d/socket.io/1/" % (host, port))
		if u.getcode() == 200:
			response = u.readline()
			(sid, hbtimeout, ctimeout, supported) = response.split(":")
			supportedlist = supported.split(",")
			if "websocket" in supportedlist:
				return (sid, hbtimeout, ctimeout)
			else:
				raise TransportException()
		else:
			raise InvalidResponseException()
 
	def connect(self):
		try:
			(sid, hbtimeout, ctimeout) = self.handshake(self.HOST, self.PORT) #handshaking according to socket.io spec.
			self.ws = websocket.create_connection("ws://%s:%d/socket.io/1/websocket/%s" % (self.HOST, self.PORT, sid))
		except Exception as e:
			print e
			sys.exit(1)

	def on(self, event, function):
		self.event_handler[event] = function

	def heartbeat(self):
		self.ws.send("2::")

	def emit(self,event,data):
		data = json.dumps(data)
		message = '5:::{"name":"%s","args":[%s]}' % (event, data)
		self.ws.send(message)

	def ready(self):
		to_read, wlist, xlist = select.select([self.ws.sock], [], [], 0.05)
		return (len(to_read) > 0)

	def join(self, data):
		self.emit("join_room", data)

	def send(self, message):
		self.ws.send(message)

	def close(self):
		self.ws.close()

	def parse_msg(self, msg):
		sp = msg.split(":")
		msg_type = sp[0]
		if msg_type == "0": # Disconnect
			self.event_handler["disconnect"]()
		elif msg_type == "1": # Connect
			self.event_handler["connect"]()
		elif msg_type == "2": # Heartbeat
			self.heartbeat()
		elif msg_type == "3": # Message
			pass
		elif msg_type == "4": # JSON message
			pass
		elif msg_type == "5": # Event
			data = json.loads(":".join(sp[3:]))
			self.event_handler[data["name"]](data["args"][0])
		elif msg_type == "6": # ACK
			pass
		elif msg_type == "7": # Error
			print "[SocketIO Error]: %s" % msg
		elif msg_type == "8": # Noop (No operation)
			pass

	def recv(self, parse=False):
		if self.ready():
			msg = self.ws.recv()
			if msg == "2::":
				self.heartbeat()
			if parse:
				self.parse_msg(msg)
			else:
				return msg