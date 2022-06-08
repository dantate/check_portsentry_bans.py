#!/usr/bin/python3 -O  
# Super Basic check for portsentry service running and how many bans in atcp file
# Version 1.1 - Auto-check for atcp/tcp mode
# Daniel Tate Wednesday 08-June-2022 12:48 PM
# Unlimited Modification Permitted

import os 
import psutil

log_location = "/var/lib/portsentry"

if __debug__:
    print('Debug ON')

# Detect if we are in tcp or atcp mode.  
# This script does not check UDP

for process in psutil.process_iter():
    if process.name().startswith('portsentry'):
        if ("udp" in process.cmdline()):
            continue
        elif ("-atcp" in process.cmdline()):
            mode = "atcp"
            log = log_location + "/portsentry.blocked.atcp"
            if __debug__:
                print("ATCP mode:", mode, log)
                print(process.cmdline())
        elif ("-tcp" in process.cmdline()):
            log = log_location + "/portsentry.blocked.tcp"
            mode="tcp"
            if __debug__:
                print("ATCP Not Matched, mode:", mode, log) 
                print(process.cmdline())

    
status = os.system('systemctl is-active --quiet portsentry')
if ( status != 0 ): 
    print('CRITICAL Portsentry Service is not running!') 
    exit(2) 

with open(log,'r') as tcp:
    x = len(tcp.readlines())
    if ( x < 150 ):
        print('OK', x, "| bans=%d" %x)
        tcp.close()
        exit(0)
    
    elif ( x > 150 and x < 250 ):
        print('WARN', x,"| bans=%d" %x)
        tcp.close()
        exit(1)
    else:
        print('CRITICAL', x,"| bans=%d" %x)
        tcp.close()
        exit(2)
