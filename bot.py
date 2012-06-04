#!/usr/local/bin/python
import socket, ssl, sys, time, threading

ircServer = "127.0.0.1"
ircPort = 8897
ircIsSSL = True
ircNick = "KillServ"
ircPassword = "killpenis123!"
ircChannel = "#kill"
ircKillReason = "Killed!"
ircCommandPrefix = "!"
ircHopDelay = 240 #seconds
ircIgnoreModes = ["o", "I"] #ignore users with these modes
ircOperUser = "KillServ"
ircOperPassword = "derp"

hopTimers = {}
channelUsers = {}

#get socket set up
ircSocket = socket.socket()
#try to connect
try:
	ircSocket.connect((ircServer, ircPort))
except Exception as e:
	print "[Error] Unable to connect to '" + ircServer + "'."
	print e
	sys.exit(0)
#if ssl is true use ssl
if ircIsSSL == True:
	ircSocket = ssl.wrap_socket(ircSocket)
print "[Info] Sucessfully connected."

#used to make sending lines easier
def writer(text):
	text = str(text).replace("\r", "").replace("\n", "")
	ircSocket.write(text + "\r\n")
	print text
	
#used to hop after set delay
def hopAfterDelay(nick):
	time.sleep(ircHopDelay)
	writer("MODE " + ircChannel + " +h " + nick)
	writer("PRIVMSG " + ircChannel + " :User " + nick + " can now kill users with no level but cannot be killed!")
	 
#get nickname from PRIVMSG
def getNick(line):
	linesplit = line.split()
	nickname = ""
	try:
		try:
			nickname = line.split()[0].split("!")[0].replace(":", "", 1)
		except:
			nickname = line.split()[0].split(".")[0].replace(":", "", 1)
		return nickname
	except:
		return ""

#send client info
writer("USER " + ircNick + " - - :Kill Bot")
writer("NICK " + ircNick)

#read incoming lines and react appropriately
inputfile = ircSocket.makefile()
while 1:
	line = inputfile.readline()
	if len(line) > 0:
		print line.strip()
		linesplit = line.split()
		if linesplit[0] == "PING":
			writer("PONG " + linesplit[1])
		if len(linesplit) > 1:
			if linesplit[1] == "001":
				writer("PRIVMSG nickserv :identify " + ircPassword)
				writer("OPER " + ircOperUser + " " + ircOperPassword)
				writer("JOIN " + ircChannel)
			if linesplit[1] == "353":
				linesplit[5] = linesplit[5].replace(":", "", 1)
				for user in linesplit[5:]:
					status = ""
					if (user.startswith("+")) or (user.startswith("%")) or (user.startswith("@")) or (user.startswith("&")) or (user.startswith("~")):
						status = user[:1]
						user = user.replace(user[:1], "", 1)
					channelUsers[user] = status
			if linesplit[1] == "JOIN":
				if linesplit[2].replace(":", "", 1) == ircChannel:
					nick = getNick(line).lower()
					channelUsers[nick] = ""
					writer("WHOIS " + nick)
			if linesplit[1] == "PART":
				if linesplit[2].replace(":", "", 1) == ircChannel:
					nick = getNick(line).lower()
					if nick in channelUsers:
						del channelUsers[nick]
					if nick in hopTimers:
						hopTimers[nick]._Thread__stop()
			if linesplit[1] == "QUIT":
				nick = getNick(line).lower()
				if nick in channelUsers:
					del channelUsers[nick]
				if nick in hopTimers:
					hopTimers[nick]._Thread__stop()
			if linesplit[1] == "379":
				ignore = False
				for mode in ircIgnoreModes:
					if mode in linesplit[7]:
						ignore = True
				if ignore == False:
					newThread = threading.Thread(target=hopAfterDelay, args=(linesplit[3],))
					hopTimers[linesplit[3].lower()] = newThread
					hopTimers[linesplit[3].lower()].start()
					writer("NOTICE " + linesplit[3] + " :Please wait " + str(ircHopDelay) + " seconds until you can't be killed and can kill users without a level!")
				else:
					writer("MODE " + ircChannel + " +h " + linesplit[3])
			if linesplit[1] == "MODE":
				if linesplit[2] == ircChannel:
					linesplit[4] = linesplit[4].lower()
					if linesplit[3].startswith("+"):
						if "v" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]] + "v"
						if "h" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]] + "h"
						if "o" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]] + "o"
						if "a" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]] + "a"
						if "q" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]] + "q"
						if linesplit[4] in hopTimers:
							hopTimers[linesplit[4]]._Thread__stop()
					if linesplit[3].startswith("-"):
						if "v" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]].replace("v", "")
						if "h" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]].replace("h", "")
						if "o" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]].replace("o", "")
						if "a" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]].replace("a", "")
						if "q" in linesplit[3]:
							channelUsers[linesplit[4]] = channelUsers[linesplit[4]].replace("q", "")
			if linesplit[1] == "PRIVMSG":
				nick = getNick(line).lower()
				if linesplit[3] == ":" + ircCommandPrefix + "kill":
					if len(linesplit) > 4:
						if len(channelUsers[nick]) > 0:
							if linesplit[4].lower() in channelUsers:
								if len(channelUsers[linesplit[4].lower()]) == 0:
									writer("KILL " + linesplit[4] + " :" + ircKillReason)
								else:
									writer("NOTICE " + nick + " :You cannot kill that user.")
							else:
								writer("NOTICE " + nick + " :That user is not in this channel.")
						else:
							writer("NOTICE " + nick + " :You do not have permission to do this until you have acquired a level in this channel.")
					else:
						writer("NOTICE " + nick + " :Not enough parameters.")
	else:
		print "[Error] Disconnected."
		break
		
