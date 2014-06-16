# !/usr/bin/python
# -*- coding: utf8 -*-

import conf, re, string, socket, sys
from room import *

# Avoid creating .pyc files
sys.dont_write_bytecode = True

# <Client> -----------------------------------------------------------------
class Client():
	def __init__(self, irc=None):
		self.linesep = re.compile(r"\r?\n")
		self.motdfile = u"motd.txt"
		self.has_quit = False

		self.user = u"User"
		self.host = u"Eclypsia.chat"
		self.irc_nick = ""
		self.irc_sock = irc

		self.ec_nick = u""
		self.ec_uid = u""
		self.ec_salt = u""
		self.ec_rights = None
		# ec_rooms = {"roomID":room_sock, ...}
		self.ec_rooms = {}

		self.banned = False
		self.rights = []
		self.superAdmin = False
		self.slowMode = False

		self.set_handlers()

	def is_connected_to(self, chan):
		chan = chan.replace("#", "")
		return chan in self.ec_rooms

	def nick(self, irc_nick, ec_nick):
		if irc_nick != self.irc_nick or ec_nick != self.ec_nick:
			self.irc_nick = irc_nick
			self.ec_nick = ec_nick
			self.reply(u"NICK %s" % (irc_nick))

	def close(self):
		for roomID, room in self.ec_rooms.items():
			room.th.stop()
		self.irc_sock.close()
		self.has_quit = True

	def join(self, chan):
		# roomID can be the rooms number
		# or a predefined alias (conf.py)
		chan = chan.replace("#", "")
		if chan not in self.ec_rooms:
			if chan.lower() in conf.aliases:
				roomID = conf.aliases[chan.lower()]
				if (conf.aliases[chan].decode().isnumeric()):
					self.ec_rooms[chan] = Room(self, roomID, chan)
				else:
					self.num_reply(u"403", u"#%s :No such channel, please check your configuration file, your alias don't match a valied roomID" % chan)
			elif chan.decode().isnumeric():
				self.ec_rooms[chan] = Room(self, chan, chan)
			else:
				self.num_reply(u"403", u"#%s :No such channel, try with a number or a predefined alias" % chan)

# IRC data handling
	def parse_msg(self, msg):
		# split selon le separateur
		lines = self.linesep.split(msg)

		# lines[:-1] = tout sauf le dernier qui est une chaîne vide
		for line in lines[:-1]:
			if self.has_quit:
				break
			if not line:
				#ligne vide
				continue
			x = line.split(" ", 1)
			command = x[0].upper()
			if len(x) == 1:
				args = []
			else:
				if len(x[1]) > 0 and x[1][0] == ":":
					args = [x[1][1:]]
				else:
					y = string.split(x[1], " :", 1)
					args = string.split(y[0])
					if len(y) == 2:
						args.append(y[1])
			self.handle_cmd(command, args)

	def handle_cmd(self, cmd, args):
		try:
			self.command_handlers[cmd](cmd, args)
		except KeyError:
			self.num_reply(u"421", "%s :Unknown command" % (cmd))

# IRC handlers
	def user_handler(self, cmd, args):
		print "\t(%s) connected" % args[0]
		self.user = args[0]
		self.num_reply(u"001", u":Hi welcome to IRC, un endroit qu'il vaut mieux éviter")
		self.num_reply(u"002", u":Your host is Localhost, running version HQN-0.1")
		self.num_reply(u"003", u":This server was created sometime")
		self.num_reply(u"004", u":Localhost HQN-0.1")
		self.num_reply(u"251", u":There are 3 million users and 0 services on 1 server")
		self.send_motd()

	def nick_handler(self, cmd, args):
		if len(self.ec_rooms) == 0:
			self.nick(args[0], "")

	def join_handler(self, cmd, args):
		if len(args) > 0:
			chans = args[0].split(",")
			for chan in chans:
				self.join(chan)

	def privmsg_handler(self, cmd, args):
		if self.is_connected_to(args[0]):
			self.ec_rooms[args[0].replace("#", "")].ec_send(u"send_chat_message", args[1])

	def quit_handler(self, cmd, args):
		print "\t(%s) disconnected" % self.user
		self.close()

	def part_handler(self, cmd, args):
		chan = args[0].replace("#", "")
		if chan in self.ec_rooms:
			room = self.ec_rooms[chan]
			room.th.stop()
			del self.ec_rooms[chan]

	def auth_handler(self, cmd, args):
		if len(args) == 2:
			# L'uid doit être un nombre
			if not args[0].decode().isnumeric():
				msg = u"Erreur lors de l'authentification, votre userID doit être un nombre"
				self.privmsg(self.irc_nick, "[AUTH]", msg)
				return
			self.ec_uid = args[0]
			self.ec_salt = args[1]
			msg = u"Vous êtes maintenant authentifié, uid: %s, salt: %s" % (self.ec_uid, self.ec_salt)
			self.privmsg(self.irc_nick, "[AUTH]", msg)

	def kick_handler(self, cmd, args):
		room = args[0].replace("#", "")
		user = args[1]
		reason = ""
		if len(args) > 2:
			reason = args[2]
		if room in self.ec_rooms:
			self.ec_rooms[room].ec_kick(user, reason)

	def ban_handler(self, cmd, args):
		pass

	def slow_handler(self, cmd, args):
		pass

	def ping_handler(self, cmd, args):
		self.send(u":%s PONG :%s" % (self.irc_nick, args[0]))

	def who_handler(self, cmd, args):
		if len(args) < 1:
			return
		target = args[0].replace("#", "")
		if target in self.ec_rooms:
			room = self.ec_rooms[target]
			room.ec_get_userslist(room.ec_who)

	def mode_handler(self, cmd, args):
		if len(args) > 2:
			room = args[0].replace("#", "")
			mode = args[1]
			user = args[2]
			if mode == "+b":
				if room in self.ec_rooms:
					self.ec_rooms[room].ban(user)

	def ison_handler(self, cmd, args):
		pass

	def set_handlers(self):
		self.command_handlers = {
				"USER" 		: self.user_handler,
				"NICK" 		: self.nick_handler,
				"JOIN" 		: self.join_handler,
				"PRIVMSG" 	: self.privmsg_handler,
				"QUIT" 		: self.quit_handler,
				"PART" 		: self.part_handler,
				"AUTH" 		: self.auth_handler,
				"KICK" 		: self.kick_handler,
				"BAN" 		: self.ban_handler,
				"SLOW" 		: self.slow_handler,
				"PING" 		: self.ping_handler,
				"WHO" 		: self.who_handler,
				"MODE" 		: self.mode_handler,
				"AUTH"		: self.auth_handler,
				"ISON"		: self.ison_handler
			}

# send over IRC socket
	def send_motd(self):
		if self.motdfile:
			try:
				lines = open(self.motdfile).readlines()
				self.num_reply(u"375", u":- Localhost Message of the day")
				for line in lines:
					self.num_reply(u"372", u":- %s" % line.decode("utf-8"))
				self.num_reply(u"376", u":End of /MOTD command")
			except IOError:
				self.num_reply(u"422", u":MOTD File is missing")
		else:
			self.num_reply(u"422", u":MOTD File is missing")
		
	def topic(self, chan, topic):
		self.num_reply(u"332", u"#%s %s" % (chan, topic))

	def part(self, user, chan, reason):
		self.send(u":%s PART %s :%s" % (user, chan, reason))

	def quit(self, user, chan, reason):
		self.send(u":%s QUIT %s :%s" % (user, chan, reason))

	def send_slice(self, msg):
		if self.irc_sock:
			message = "%s" % msg
			message = message.encode("utf-8")
			self.irc_sock.send(message)

	def send(self, msg):
		try:
			if self.irc_sock:
				msg = msg.replace("\n", "")
				msg = msg.replace("\r", "")
				message = "%s\r\n" % msg
				message = message.encode("utf-8")
				self.irc_sock.send(message)
		except socket.error as serr:
			self.close()

	def reply(self, msg):
		if self.irc_sock:
			message = ":%s %s\r\n" % (self.irc_nick, msg)
			message = message.encode("utf-8")
			self.irc_sock.send(message)

	def num_reply(self, num, msg):
		# ":Nick 324 Nick #ectv +t\r\n"
		if self.irc_sock:
			message = ":%s %s %s %s\r\n" % (self.irc_nick, num, self.irc_nick, msg)
			message = message.encode("utf-8")
			self.irc_sock.send(message)

	def joined(self, target, source):
		self.send(u":%s JOIN %s" % (source, target))

	def privmsg(self, target, source, msg):
		message = u":%s PRIVMSG %s :%s" % (source, target, msg)
		self.send(message)

	def kick(self, user, target, reason):
		self.send(u":[SERVER] KICK %s %s :%s" % (target, user, reason))

	def ban(self, user, target, reason):
		self.send(u":[SERVER] MODE %s +b %s" % (target, user))
		self.kick(user, target, reason)

# </Client> ----------------------------------------------------------------