# !/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket, select
import string
import re
import conf
from client import *
from socketIO_client import SocketIO

irc_host = ''

# <Server> -----------------------------------------------------------------
class Server():
	def __init__(self, ports):
		self.ports = ports
		# socks [sock1, sock2, ...]
		self.socks = []
		# rooms {"RoomName": socket}
		self.rooms = {
			"#ectv" : None,
			"#ectv2" : None
		}

		for port in self.ports:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.bind((irc_host, port))
			sock.listen(5)
			self.socks.append(sock)
		print("Serveur UP, port(s): %s" % self.ports)

	def start(self):
		self.clients = {}
		while True:
			new_clients, wlist, xlist = select.select(self.socks,
				[], [], 0.10)

			for client in new_clients:
				sock, infos = client.accept()
				print u"Nouveau client:"
				print infos
				# On ajoute la socket connectée à la liste des clients
				self.clients[sock] = Client(irc=sock)

			clients_a_lire = []
			try:
				clients_a_lire, wlist, xlist = select.select(self.clients,
						[], [], 0.05)
			except select.error:
				pass
			else:
				# On parcourt la liste des clients à lire
				for client in clients_a_lire:
					msg_recu = client.recv(1024)
					msg_recu = msg_recu.decode("utf8")
					self.clients[client].parse_msg(msg_recu)
					if self.clients[client].has_quit:
						del self.clients[client]

		print("Fermeture des connexions")
		for client in self.clients:
			client.close()
		connexion_principale.close()

	def del_client(self, client_sock):
		del self.clients[client_sock]

# </Server> ----------------------------------------------------------------

if __name__ == "__main__":
	serv = Server(conf.irc_ports)
	serv.start()
