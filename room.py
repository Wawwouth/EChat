# !/usr/bin/python
# -*- coding: utf-8 -*-

from socketIO import *
import re, sys
import conf
import threading
import logging

# Avoid creating .pyc files
sys.dont_write_bytecode = True

class SockThread(threading.Thread):
	def __init__(self, sock):
		threading.Thread.__init__ (self)
		self.sock = sock
		self.Terminated = False

	def run(self):
		while(not self.Terminated):
			self.sock.recv(True)
		self.sock.close()

	def stop(self):
		self.Terminated = True

# <Room>--------------------------------------------------------------------
class Room():
	def __init__(self, owner, roomID="23", alias=""):
		# self.status_reg = re.compile('User has been (.*)\.(\ .*)?')
		self.status_reg = re.compile(u"L'utilisateur a été (.*)\.(\ .*)?")
		self.owner = owner
		self.id = roomID
		self.alias = alias
		self.connected = False

		self.members = {}
		self.topic = ""
		self.write_buffer = ["", ""]
		if alias == "ectv" or roomID == conf.aliases["ectv"]:
			self.s = SocketIO(conf.ec_host, conf.ec_port1)
		elif alias == "ectv2" or roomID == conf.alias["ectv2"]:
			self.s = SocketIO(conf.ec_host, conf.ec_port2)
		else: 
			self.s = SocketIO(conf.ec_host, conf.ec_port_affiliate)
		self.set_handlers()
		self.th = SockThread(self.s)
		self.th.start()

	def ec_send(self, event, msg):
		if self.s:
			self.s.emit(event, {'message': self.spacify(msg), 'roomID': self.id, 'colorNickname': "000000"})

	def ec_join(self):
		if self.s:
			join_data = {'roomID': self.id, 'userID': self.owner.ec_uid, 'salt': self.owner.ec_salt}
			self.s.emit("join_room", join_data)

	def ec_kick(self, nick, reason):
		message = "/kick '%s' %s" % (self.spacify(nick), reason)
		self.ec_send("send_chat_message", message)

	def ec_ban(self, nick):
		message = "/ban '%s'" % self.spacify(nick)
		self.ec_send("send_chat_message", message)

	def ec_slow(self, roomID, nick, delay="10"):
		message = "/slow '%s' %s" % (self.spacify(nick), delay)
		self.ec_send(roomID, msg_event, message)

	def ec_get_userslist(self, fun):
		if self.s:
			self.s.emit("get_userlist", {'roomID': self.id}, fun)

	def ec_refresh_userslist(self):
		self.ec_get_userslist(self.on_ec_refresh_userlist)

	def ec_who(self, usersList):
		for uid in usersList:
			self.owner.num_reply(u"352", u"#%s ECUser EclypsiaChat Localhost %s H :0 %s" % (self.alias, usersList[uid], uid))
		self.owner.num_reply(u"315", u":End of WHO list")

	def left(self, client):
		del self.members[client.irc_sock]
		for c in self.members:
			c.send("%s PART #%s :left" % (client.irc_nick, self.id))

	# replace spaces in nicknames
	def unspacify(self, nick):
		return nick.replace(" ", "`")

	# reset spaces in nicknames
	def spacify(self, nick):
		return nick.replace("`", " ")

	# delete color tags from message
	def uncolor(self, msg):
		p = re.compile("\[color=(.*)\](.*)\[\/color\]")
		r = p.match(msg)
		if r:
			return r.group(2)
		return msg

	def rand_part_msg(self):
		return "Tard+"

# ------------- HANDLERS --------------------
	def on_ec_connect(self):
		self.ec_join()
	
	def on_ec_connecting(self):
		pass
	
	def on_ec_connect_failed(self):
		pass
	
	def on_ec_reconnect(self):
		pass
	
	def on_ec_reconnecting(self):
		pass
	
	def on_ec_reconnect_failed(self):
		pass
	
	def on_ec_disconnect(self):
		self.owner.part(self.owner.irc_nick, "#%s" % self.alias, "Disconnected")
	
	def on_ec_error(self):
		pass

	def on_ec_receive_chat_message(self, data):
		if data["username"] != self.owner.ec_nick:
			user = self.unspacify(data["username"])
			target = "#%s" % self.alias
			source = ""
			if (data["rights"] != ""):
				source += "[%s]:" % data["rights"]
			source += user
			msg = data["message"]
			self.owner.privmsg(target, source, msg)
	
	def on_ec_receive_status_message(self, data):
		user = data["username"]
		target = "#%s" % self.alias

		source = "[SERVER]"
		color = "\0034"
		msg = "%s(%s) %s" % (color, user, data["message"])
		self.owner.privmsg(target, source, msg)

	def on_ec_receive_tips_message(self, data):
		target = "#%s" % self.alias
		source = "[TIPS]"
		tips_color = "\0033"
		msg = u"%s(%s) a envoyé %s tips: { %s }" % (tips_color, data["username"], data["amount"], data["message"])

		self.owner.privmsg(target, source, msg)
	
	def on_ec_init_connexion(self, data):
		# banned, ignorable, previousMessage, rights, slowMode, superAdmin(bool)
		self.userInfo = data["userInfo"]
		self.owner.nick(irc_nick=self.unspacify(self.userInfo["username"]) ,ec_nick=self.userInfo["username"])
		self.owner.banned = self.userInfo["banned"]
		self.owner.rights = self.userInfo["rights"]
		self.owner.slowMode = self.userInfo["slowMode"]
		self.owner.joined("#%s" % self.alias, self.owner.irc_nick)
		
		# roomID, slowMode, welcomeMessage
		self.roomData = data["roomData"]
		self.id = self.roomData["roomID"]
		self.topic = "%s | slowMode: '%s'" % (self.roomData["welcomeMessage"], self.roomData["slowMode"])
		self.owner.topic(self.alias, self.topic)

		self.ec_refresh_userslist()
	
	def on_ec_init_connexion_anonymous(self, data):
		msg = u"Vous êtes connectés en tant qu'anonyme, authentifiez vous pour avoir accès à la liste des utilisateurs"
		# roomID, slowMode, welcomeMessage
		self.roomData = data["roomData"]
		self.id = self.roomData["roomID"]
		self.topic = self.roomData["welcomeMessage"]
		self.owner.topic(self.alias, self.topic)

		# banned, ignorable, previousMessage, rights, slowMode, superAdmin(bool), 
		self.userInfo = data["userInfo"]
		self.owner.banned = self.userInfo["banned"]
		self.owner.rights = self.userInfo["rights"]
		self.owner.slowMode = self.userInfo["slowMode"]
		self.owner.joined("#%s" % self.alias, self.owner.irc_nick)
	
	def on_ec_user_join(self, data):
		target = "#%s" % self.alias
		source = self.unspacify(data["username"])
		if source != self.owner.irc_nick:
			self.owner.joined(target, source)
	
	def on_ec_user_leave(self, data):
		target = target = "#%s" % self.alias
		source = self.unspacify(data["username"])
		if source != self.owner.irc_nick:
			self.owner.part(source, target, self.rand_part_msg())
	
	def on_ec_activate_chat(self):
		# nothing
		pass

	def on_ec_deactivate_chat(self):
		# nothing
		pass

	def on_ec_enable_chat(self):
		# nothing
		pass

	def on_ec_disable_chat(self):
		# nothing
		pass

	def on_ec_set_header(self, data):
		self.owner.topic(self.alias, data)

	def on_ec_refresh_userlist(self, data):
		for uid, nick in data.items():
			self.owner.num_reply("353", "= #%s :%s" % (self.alias, self.unspacify(nick)))
		self.owner.num_reply("366", "#%s :End of NAMES list" % self.alias)

	def set_handlers(self):
		eventHandlers = {
				'connecting' : self.on_ec_connecting,
				'receive_chat_message' : self. on_ec_receive_chat_message,
				'receive_status_message' : self.on_ec_receive_status_message,
				'receive_tips_message' : self.on_ec_receive_tips_message,
				'connect_failed' : self.on_ec_connect_failed,
				'error' : self.on_ec_error,
				'reconnect_failed' : self.on_ec_reconnect_failed,
				'reconnect' : self.on_ec_reconnect,
				'reconnecting' : self.on_ec_reconnecting,
				'connect' : self.on_ec_connect,
				'enable_chat' : self.on_ec_enable_chat,
				'disable_chat' : self.on_ec_disable_chat,
				'activate_chat' : self.on_ec_activate_chat,
				'deactivate_chat' : self.on_ec_deactivate_chat,
				'user_join' : self.on_ec_user_join,
				'user_leave' : self.on_ec_user_leave,
				'init_connexion' : self.on_ec_init_connexion,
				'init_connexion_anonymous' : self.on_ec_init_connexion_anonymous,
				'set_header' : self.on_ec_set_header,
				'refresh_userlist' : self.on_ec_refresh_userlist
			}
		for event in eventHandlers:
			self.s.on(event, eventHandlers[event])


# ------------- HANDLERS --------------------

# </Room>-------------------------------------------------------------------