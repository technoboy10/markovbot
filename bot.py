#!/usr/bin/env python
# A simple Python bot to tell jokes.
# For hardmath123.github.io/socket-science-2.html

import socket
import select
import ssl
import sys
import time
import random
import urllib
from pymarkovchain import *
from bs4 import BeautifulSoup as Soup

if len(sys.argv) != 6:
    print "Usage: python %s <host> <password> <channel> [--ssl|--plain] <nick>"
    exit(0)

HOST = sys.argv[1]
PASS = sys.argv[2]
CHANNEL = "#"+sys.argv[3]
SSL = sys.argv[4].lower() == '--ssl'
PORT = 6697 if SSL else 6667

NICK = sys.argv[5]

plain = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = ssl.wrap_socket(plain) if SSL else plain

print "Connecting..."

m = MarkovChain('irc2')
db = open("db.txt", "r").read()

s.connect((HOST, PORT))
def read_loop(callback):
    data = ""
    CRLF = '\r\n'
    while True:
        try:
            readables, writables, exceptionals = select.select([s], [s], [s]) 
            if len(readables) == 1:
                data += s.recv(512);
                while CRLF in data:
                    message = data[:data.index(CRLF)]
                    data = data[data.index(CRLF)+2:]
                    callback(message)
        except KeyboardInterrupt:
            print "Leaving..."
            s.sendall("PART %s :Bye\r\n"%(CHANNEL))
            s.close()
            exit(0)
        time.sleep(0.5)

print "Registering..."

s.sendall("PASS %s\r\n"%PASS)
s.sendall("NICK %s\r\n"%(NICK))
s.sendall("USER %s * * :tb10\r\n"%(NICK))


connected = False
def got_message(message):
    print message
    global connected # yes, bad Python style. but it works to explain the concept, right?
    global db # this too :P   
    words = message.split(' ')
    if 'PING' in message:
        s.sendall('PONG\r\n') # it never hurts to do this :)
    if words[1] == '001' and not connected:
        # As per section 5.1 of the RFC, 001 is the numeric response for
        # a successful connection/welcome message.
        connected = True
        s.sendall("JOIN %s\r\n"%(CHANNEL))
        print "Joining..."
    elif words[1] == 'PRIVMSG' and words[2] == CHANNEL and connected:
        # Someone probably said something.
        if '!markov' in words[3]:
            m.generateDatabase(db)
            s.sendall("PRIVMSG %s :"%(CHANNEL) + m.generateString() + "\r\n")
        #elif '!web' in words[3]:
         #   db += Soup(urllib.urlopen(words[4]).read()).get_text().encode("utf-8") + " "            
          #  s.sendall("PRIVMSG %S :"%(CHANNEL) + "k, added %s"%(words[4]) + "\r\n")"""
        else:
           # try:
            db += message.split(CHANNEL + " :")[1]
            db += " "
            open('db.txt', 'w').write(db)
     
            if (random.choice(list(range(0,10))) == 1):
                s.sendall("PRIVMSG %s :"%(CHANNEL) + random.choice(["!moose", "!joke"]) + "\r\n")           

read_loop(got_message)
