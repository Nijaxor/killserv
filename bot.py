#!/usr/local/bin/python
import socket, ssl, sys, time, threading

ircServer = "irc.server.net"
ircPort = 6697
ircIsSSL = True
ircNick = "KillServ"
ircPassword = "password"
ircChannel = "#kill"
ircKillReason = "Killed!"
ircCommandPrefix = "!"
ircHopDelay = 240 #seconds
ircUnBanDelay = 240 #seconds
ircIgnoreModes = ["o", "I"] #ignore users with these modes
ircOperUser = "KillServ"
ircOperPassword = "password"

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
def hopAfterDelay(a):
	time.sleep(ircHopDelay)
	if a[1] == True:
		writer("MODE " + ircChannel + " +h " + a[0])
		writer("PRIVMSG " + ircChannel + " :User " + a[0] + " can now kill users that don't have a level but cannot be killed!")

#used to unban after set dely
def unBanAfterDelay(nick):
	time.sleep(ircUnBanDelay0
	writer("MODE " + ircChannel + " -b " + a)
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
		#ping/pong
		if linesplit[0] == "PING":
			writer("PONG " + linesplit[1])
		if len(linesplit) > 1:
			#on connect
			if linesplit[1] == "001":
				writer("PRIVMSG nickserv :identify " + ircPassword)
				writer("OPER " + ircOperUser + " " + ircOperPassword)
				writer("JOIN " + ircChannel)
			#channel users
			if linesplit[1] == "353":
				linesplit[5] = linesplit[5].replace(":", "", 1)
				for user in linesplit[5:]:
					status = ""
					if user.startswith("+"):
						status = status + "v"
					if user.startswith("%"):
						status = status + "h"
					if user.startswith("@"):
						status = status + "o"
					if user.startswith("&"):
						status = status + "ao"
					if user.startswith("~"):
						status = status + "q"
					user = user.replace(user[:1], "", 1).lower()
					channelUsers[user] = status
				print channelUsers
			#process joins
			if linesplit[1] == "JOIN":
				if linesplit[2].replace(":", "", 1) == ircChannel:
					nick = getNick(line).lower()
					if not nick == ircNick:
						channelUsers[nick] = ""
						writer("WHOIS " + nick)
			#process parts
			if linesplit[1] == "PART":
				if linesplit[2].replace(":", "", 1) == ircChannel:
					nick = getNick(line).lower()
					if nick in channelUsers:
						del channelUsers[nick]
					if nick in hopTimers:
						hopTimers[nick][1] = False
			#process quits
			if linesplit[1] == "QUIT":
				nick = getNick(line).lower()
				if nick in channelUsers:
					del channelUsers[nick]
				if nick in hopTimers:
					hopTimers[nick][1] = False
			#process nick changes
			if linesplit[1] == "NICK":
				nick = getNick(line).lower()
				newNick = linesplit[2].replace(":", "", 1)
				if nick in channelUsers:
					channelUsers[newNick.lower()] = channelUsers[nick]
					del channelUsers[nick]
					if nick.lower() in hopTimers:
						hopTimers[newNick.lower()] = hopTimers[nick.lower()]
						hopTimers[newNick.lower()][0] = newNick
						del hopTimers[nick.lower()]
			#looking for ignore modes
			if linesplit[1] == "379":
				ignore = False
				for mode in ircIgnoreModes:
					if mode in linesplit[7]:
						ignore = True
				if ignore == False:
					hopTimers[linesplit[3].lower()] = [linesplit[3], True]
					newThread = threading.Thread(target=hopAfterDelay, args=(hopTimers[linesplit[3].lower()],))
					newThread.start()
					writer("NOTICE " + linesplit[3] + " :Please wait " + str(ircHopDelay) + " seconds before you can't be killed and can kill users that don't have a level!")
				else:
					writer("MODE " + ircChannel + " +h " + linesplit[3])
			#handle change in modes
			if linesplit[1] == "MODE":
				if linesplit[2] == ircChannel:
					normalNick = linesplit[4]
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
							hopTimers[linesplit[4]][1] = False
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
						if len(channelUsers[linesplit[4]]) == 0:
							hopTimers[linesplit[4]] = [normalNick, True]
							newThread = threading.Thread(target=hopAfterDelay, args=(hopTimers[linesplit[4]],))
							newThread.start()
							writer("NOTICE " + linesplit[4] + " :Please wait " + str(ircHopDelay) + " seconds before you can't be killed and can kill users that don't have a level!")
			#process privmsgs
			if linesplit[1] == "PRIVMSG":
				nick = getNick(line).lower()
				if linesplit[3] == ":" + ircCommandPrefix + "kill":
					if len(linesplit) > 4:
						if len(channelUsers[nick]) > 0:
							if linesplit[4].lower() in channelUsers:
								if len(channelUsers[linesplit[4].lower()]) == 0:
									writer("MODE " + ircChannel + " +b " + linesplit[4])
									unBanAfterDelay(linesplit[4])
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
		
