# !/usr/bin/python
# -*- coding: utf-8 -*-

import conf, re

tips_color = "\00303"
op_color = "\00302"
server_color = "\00304"

op_regex = re.compile("^\[((S?ADMIN)|MOD)\](.*)")

def tips_test(client, cmd, args):
	if len(args) > 0:
		target = args[0]
		source = "[TIPS]"
		msg = "Ceci est un message de test"
		client.privmsg(target, source, msg)

def admin_test(client, cmd, args):
	if len(args) > 0:
		target = args[0]
		source = "[ADMIN]Test"
		msg = "Ceci est un message de test"
		client.privmsg(target, source, msg)

def serv_test(client, cmd, args):
	if len(args) > 0:
		target = args[0]
		source = "[SERVER]"
		msg = "Ceci est un message de test"
		client.privmsg(target, source, msg)

def init():
	print "initializing test_cmds module ..."
	hooks = { 	"tipstest" : tips_test,
				"admintest" : admin_test,
				"servtest" : serv_test
			}
	for cmd, hook in hooks.items():
		conf.add_out_hook(cmd, hook)