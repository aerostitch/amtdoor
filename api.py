#!/usr/bin/env python3
'''
This is an API to use on the RFID validation and update for the doors at AMT.
It's written to be extended to whatever other use we could have.
Endpoints:
  - /rfid/<the_rfid_to_check>: will return if yes or no the rfid is authorized
    based on the rfid.inc file
  - /rfids/update: will update the rfid.inc file by calling the url
'''

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

LISTENER_IP = "0.0.0.0"
HOST_PORT = 9000

class MyServer(BaseHTTPRequestHandler):
    '''
    Class that handles the HTTP requests of the server
    '''

    def check_rfid(self, rfid):
        '''
        Checks if the RFID is in the list of valid ones
        '''
        try:
            valid_cards = open('rfid.inc', 'r').read().strip().split('\n')
        except Exception:
            return {'error': 'Unable to get the rfdi informations from the database'}
        # Default behavior: not valid
        return {'valid_rfid': rfid in valid_cards}

    def update_rfids(self):
        '''
        Updates the rfid.inc file form the url
        '''
        return {'error': 'Not implemented yet'}

    def process_request(self):
        '''
        This function redirects the request to the right function
        '''
        commands = self.path.strip('/').split('/')
        if len(commands) == 2:
            if commands[0] == 'rfid':
                # This part checks that a RFID is valid from the log file
                return self.check_rfid(commands[1])
            if commands[0] == 'rfids' and commands[1] == 'update':
                # This part updates the rfid.inc file from the url
                return self.update_rfids()
        # Default path
        return {'error': "path not found %s" % self.path}

    def do_GET(self):
        '''
        Usual method catching the GET requests
        '''
        response = self.process_request()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes("%s" % json.dumps(response), "utf-8"))

if __name__ == 'main':
    myServer = HTTPServer((LISTENER_IP, HOST_PORT), MyServer)

    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass

    myServer.server_close()
