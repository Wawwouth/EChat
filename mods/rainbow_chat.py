# !/usr/bin/python
# -*- coding: utf-8 -*-

import conf, re

tips_color = "\00303"
op_color = "\00302"
server_color = "\00304"

op_regex = re.compile("^\[((S?ADMIN)|MOD)\](.*)")

def colorize_msg(target, source, msg):
	if source == "[TIPS]":
		msg = tips_color + msg
	elif source == "[SERVER]":
		msg = server_color + msg
	elif op_regex.match(source):
		msg = op_color + msg
	return (target, source, msg)

def init():
	print "initializing Rainbow_chat module ..."
	hooks = { 	"PRIVMSG" : colorize_msg
			}
	for cmd, hook in hooks.items():
		conf.add_in_hook(cmd, hook)