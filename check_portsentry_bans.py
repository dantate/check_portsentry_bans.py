#!/usr/bin/python3
# Super Basic check for portsentry service running and how many bans in atcp file

import os 


tcplog = "/var/lib/portsentry/portsentry.blocked.tcp"
tcpalog = "/var/lib/portsentry/portsentry.blocked.atcp"

status = os.system('systemctl is-active --quiet portsentry')
if ( status != 0 ): 
    print('CRITICAL Portsentry Service is not running!') 
    exit(2) 

with open(r"/var/lib/portsentry/portsentry.blocked.atcp",'r') as tcp:
    x = len(tcp.readlines())
    if ( x < 150 ):
        print('OK', x, "| bans=%d" %x)
    
    elif ( x > 150 and x < 250 ):
        print('WARN', x,"| bans=%d" %x)

    else:
        print('CRITICAL', x,"| bans=%d" %x)
    
    tcp.close()
