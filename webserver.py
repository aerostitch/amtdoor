#!/usr/bin/env python
#Copyright Jon Berg , turtlemeat.com
# Changes for AMT done by Dr. Jesus <admin@acemonstertoys.org>

import string,cgi,time,ieee1284,sys,syslog,logging,logging.handlers
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer, __version__
from mako.template import Template

def get_door_port():
    p = ieee1284.find_ports()
    p = p["parport0"]
    p.open(0)
    p.claim()
    return p

# The way this works is there's a latching relay hooked up to two of the 
# parallel port pins.  Setting pin #3 to logic high will flip the relay to
# the open state, and setting pin #1 to logic high will flip the relay to
# the closed state.
#
# The relay doesn't provide much resistance, so don't pulse the pins 
# for too long in case the protection circuitry breaks down.

def open_door():
    p = get_door_port()
    p.write_data(0x4)
    time.sleep(0.2)
    p.write_data(0x0)
    p.close()
    
def close_door():
    p = get_door_port()
    p.write_data(0x1)
    time.sleep(0.2)
    p.write_data(0x0)
    p.close()

def bounce_door_relay():
    open_door()
    time.sleep(5)
    close_door()

class StdoutRedirector(object):
    def __init__(self, name=None):
        syslog.openlog("door", 0, syslog.LOG_AUTH)
    def write(self, msg, level=syslog.LOG_INFO):
        msg = msg.rstrip('\r\n ')
        if(len(msg) == 0):
	    return
        syslog.syslog(level, msg)

class StderrRedirector(object):
    def __init__(self, name=None):
        self.logger = logging.getLogger('door')
        self.handler = logging.handlers.RotatingFileHandler('/var/log/door.log', maxBytes=1048576, backupCount=5)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)
    def write(self, msg):
        if(len(msg) == 0):
            return
        msg = msg.rstrip('\r\n ')
        self.logger.info(msg)

class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        self.message = ""
	BaseHTTPRequestHandler.__init__(self, server_address, RequestHandlerClass, bind_and_activate)

    def printpage(self):
        try:
            f = open(curdir + sep + "index.html")
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            self.wfile.write(Template(f.read()).render(message=self.message))
            f.close()
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def do_GET(self):
        self.printpage()

    def do_POST(self):
        global rootnode
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
	    if not ctype: return None
	    if ctype == 'multipart/form-data':
	    	query = cgi.parse_multipart(self.rfile, pdict)
	    elif ctype == 'application/x-www-form-urlencoded':
	    	clength = int(self.headers.get('Content-length'))
	    query = cgi.parse_qs(self.rfile.read(clength), 1)
            
	    if self.client_address[0][0:11] != "192.168.162":
		if not query.has_key('code'):
		    self.message = "Need code."
                else:
            	    theircode = query.get('code')
	    	    codefile = file('/root/.doorcode')
	    	    ourcode = codefile.read(4)
	    	    codefile.close()
            	    if theircode[0] == ourcode:
	                self.message = "Open Sesame."
            	        bounce_door_relay()
	            else:
	                self.message = "Nope."
            else:
                self.message = "Open Sesame."
            	bounce_door_relay()
            self.printpage()
            
        except Exception,e:
	    print(e.message)

def main():
    sys.stdout.close()
    sys.stdout = StdoutRedirector("door")
    sys.stderr.close()
    sys.stderr = StderrRedirector("door")
    # Let's start up with the door in a known state.
    close_door()
    try:
        server = HTTPServer(('', 80), MyHandler)
	print("Started server version %s" % __version__)
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()

