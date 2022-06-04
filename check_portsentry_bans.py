#!/usr/bin/python3
#2022 Daniel Tate
#Extremely basic check for portsentry service running, and how many entries are in the portsentry log file.

import os 
import sys
import subprocess
from subprocess import Popen


tcplog = "/var/lib/portsentry/portsentry.blocked.tcp"
tcpalog = "/var/lib/portsentry/portsentry.blocked.atcp"

status = os.system('systemctl is-active --quiet portsentry')
if ( status != 0 ): 
    print('CRITICAL Portsentry Service is not running!') 
    exit(2) 

with open(r"/var/lib/portsentry/portsentry.blocked.atcp",'r') as tcp:
    x = len(tcp.readlines())
    if ( x < 150 ):
        print('OK', x)
    
    elif ( x > 150 and x < 250 ):
        print('WARN', x)

    else:
        print('CRITICAL', x)
    
    tcp.close()
