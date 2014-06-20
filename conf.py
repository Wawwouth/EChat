# !/usr/bin/python
# -*- coding: utf-8 -*-

# mods shared vars
in_cmd_hooks = {}
out_cmd_hooks = {}

# host = "chatv2.eclypsia.com"
# ec_host = "95.142.101.119"
ec_host = "54.76.195.245"
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
			"ectv2" : "2675",
			"ircarmy" : "1337",
			"lrbtv" : "5365",
			"nanashor" : "3",
			"nanashortv" : "3",
			"velahan" : "1059",
			"jiraya" : "6",
			"mizuty" : "3080",
			"gbt" : "6495",
			"leagueofladies" : "5654",
			"nailow" : "3749",
			"le-tol" : "5356",
			"zerator" : "1"
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