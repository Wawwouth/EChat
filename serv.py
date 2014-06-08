# !/usr/bin/python
# -*- coding: utf-8 -*-

import socket, select
import conf
from client import *
from socketIO_client import SocketIO

# <Server> -----------------------------------------------------------------
class Server():
	def __init__(self, host, ports):
		self.ports = ports
		self.host = host
		# 
		self.socks = []
		for port in self.ports:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.bind((self.host, port))
			sock.listen(5)
			self.socks.append(sock)
		print("Serveur UP, port(s): %s" % self.ports)

	def start(self):
		# clients = {client_socket : Client(), ...}
		self.clients = {}
		try:
			while True:
				# Looking for new connexions
				new_clients, wlist, xlist = select.select(self.socks, [], [], 0.10)
				# Adding new clients to the list
				for client in new_clients:
					sock, infos = client.accept()
					self.clients[sock] = Client(irc=sock)

				to_read = []
				try:
					to_read, wlist, xlist = select.select(self.clients, [], [], 0.05)
				except select.error:
					pass
				else:
					# 
					for client in to_read:
						try:
							received = client.recv(1024).decode("utf8")
							self.clients[client].parse_msg(received)
							if self.clients[client].has_quit:
								del self.clients[client]
						except socket.error :
							self.clients[client].close()
							print "(%s) disconnected" % self.clients[client].user
							del self.clients[client]
		except (KeyboardInterrupt, SystemExit):
			self.stop()

	def stop(self):
		print("Arrêt du serveur...")
		for sock, client in self.clients.items():
			client.close()
		for sock in self.socks:
			sock.close()
		print "Serveur DOWN."
# </Server> ----------------------------------------------------------------

if __name__ == "__main__":
	serv = Server(conf.irc_host, conf.irc_ports)
	serv.start()
