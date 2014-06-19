# !/usr/bin/python
# -*- coding: utf-8 -*-

import socket, select, sys
from client import *
import conf
import glob, imp
from os.path import join, basename, splitext

# Avoid creating .pyc files
sys.dont_write_bytecode = True

# <Server> -----------------------------------------------------------------
class Server():
	def __init__(self, host, ports):
		self.ports = ports
		self.host = host
		# 
		self.socks = []
		for port in self.ports:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
					self.clients[sock] = Client(sock, conf.in_cmd_hooks, conf.out_cmd_hooks)

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
		for sock in self.socks:
			self.socks.remove(sock)
		print "Serveur DOWN."
# </Server> ----------------------------------------------------------------

def import_mods():
	modules = {}
	for path in glob.glob(join("mods",'[!_]*.py')): # list .py files not starting with '_'
		name, ext = splitext(basename(path))
		modules[name] = imp.load_source(name, path)
		modules[name].init()

if __name__ == "__main__":
	import_mods()
	serv = Server(conf.irc_host, conf.irc_ports)
	serv.start()
