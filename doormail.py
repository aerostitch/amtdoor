#!/usr/bin/env python
import sys
import urllib
import urllib2
import email
import email.parser
parser = email.parser.Parser()
msg = parser.parse(sys.stdin)
payload = msg.get_payload()
code = file("/home/j/.doorcode")
code = code.read(4)
if payload[0:4] == code:
	req = urllib2.Request('http://drj.broke-it.net:6050/', urllib.urlencode({"code": code}))
	resp = urllib2.urlopen(req)
