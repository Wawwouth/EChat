# !/usr/bin/python
# -*- coding: utf-8 -*-

# mods shared vars
in_cmd_hooks = {}
out_cmd_hooks = {}

# host = "chatv2.eclypsia.com"
<<<<<<< HEAD
#ec_host = "95.142.101.119"
ec_host = "node.eclypsia.com"
=======
# ec_host = "95.142.101.119"
# ec_host = "54.76.195.245"
ec_host = "54.77.18.242"
>>>>>>> 24ea7eb6d379b342c26a6b4b7448cf670e15890e
ec_port1 = 12564
ec_port2 = 12565
ec_port_affiliate = 12566

irc_host = ''
irc_ports = [6667, 6668]

join_event = "join_room"
msg_event = "send_chat_message"

# Aliases should be in lowercase
# No spaces, no special characters
# { "roomalias" : "roomID"}
aliases = { "ectv" : "23",
			"taipouz" : "17",
			"ruurk" : "189",
			"skyyart" : "5",
			"mr-freeze" : "5220",
			"clchiva" : "1346",
			"ectv2" : "2675",
			"ircarmy" : "1337",
			"lrbtv" : "5365",
			"velahan" : "1059",
			"drfeelgood" : "5212",
			"jiraya" : "6",
			"leagueofladies" : "5654",
			"zerator" : "1",
			"chelxie" : "3037",
			"maxildan" : "16",
			"aeterna" : "99",
			"kwev" : "3300",
			"ectv3" : "9442"
			}

def add_out_hook(cmd, hook):
	cmd = cmd.upper()
	if cmd in out_cmd_hooks:
		out_cmd_hooks[cmd].append(hook)
	else:
		out_cmd_hooks[cmd] = [hook]

def add_in_hook(cmd, hook):
	cmd = cmd.upper()
	if cmd in in_cmd_hooks:
		in_cmd_hooks[cmd].append(hook)
	else:
		in_cmd_hooks[cmd] = [hook]
