#!/usr/bin/python

import argparse
import re
import requests
import socket
import sys
import time

from IPy import IP

VALUES = []
VERBOSE = False

def convert(stringValue):
    split = stringValue.split(" ")
    if len(split) != 2:         return None
    split[0] = float(split[0].replace(',','.'))
    if split[1] == '%':         return (split[0], 'pct')
    if split[1] == 'w':         return (split[0], 'watt')
    if split[1].endswith('C'):  return (split[0], 'celsius')
    return (split[0], re.sub(r"[^\w\s]", '_', split[1]).lower())

def parseSensor(jsonSensor, prefix):
    prefix = prefix + '.' if prefix else ''
    parseName(jsonSensor, prefix)
    [parseSensor(child, jsonSensor['Text']) for child in jsonSensor['Children']] if len(jsonSensor['Children']) else appendValue(jsonSensor)

def parseName(jsonSensor, prefix):
    jsonSensor['Text'] = re.sub(r"[^\w\s]", '_', jsonSensor['Text'])
    jsonSensor['Text'] = re.sub(r"\s+", '_', jsonSensor['Text'])
    jsonSensor['Text'] = re.sub(r"__", '_', jsonSensor['Text'])
    jsonSensor['Text'] = "%s%s" % (prefix, jsonSensor['Text'])

def appendValue(jsonSensor):
    for v in ['Value', 'Min', 'Max']:
        c = convert(jsonSensor[v])
        if not c: continue
        VALUES.append("%s.%s.%s %s %s" % (jsonSensor['Text'], c[1], v, c[0], int(time.time())));

def reportToCarbon(addr, port):
    try:
        IP(addr)  # Verify if IP is valid
    except:
        addr = socket.gethostbyname(addr)

    try:
        sock = socket.socket()
        sock.connect((addr, port))
        sock.sendall('\n'.join(VALUES))
        sock.close()
        if VERBOSE: print '\n'.join(VALUES)
    except Exception as e:
        if VERBOSE: print "FATAL: Failed connecting to Carbon server\n%s" % e
        sys.exit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get host information from Open Hardware Monitor and report it Carbon (i.e. Graphite)')
    parser.add_argument('--host', help='Name/IP of host running OHW', required=True)
    parser.add_argument('--port', help='Port OHW is listening on [default: 8085]', default=8085)
    parser.add_argument('--graphite-host', help='Name/IP of host running Carbon', required=True)
    parser.add_argument('--graphite-port', help='Port Carbon is listening on [default: 2003]', default=2003)
    parser.add_argument('--verbose', help='Enable/Diasble all CLI output (inluding errors) [default: false]', action='store_true')
    args = vars(parser.parse_args())

    VERBOSE = args['verbose']
    
    try:
        r = requests.get("http://%s:%s/data.json" % (args['host'], args['port']))
        r.raise_for_status()
    except Exception as e:
        if VERBOSE: print "FATAL: Failed requesting JSON data\n%s" % e
        sys.exit(1)
    jsonValues = r.json()
    parseSensor(jsonValues['Children'][0], None)
    reportToCarbon(args['graphite_host'], args['graphite_port'])
