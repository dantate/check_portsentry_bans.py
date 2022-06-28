#!/usr/bin/python3
# Super Basic check for portsentry service running and how many bans in atcp file
# Relies on portsentry being run by (or at least accessable to) systemd.
# Requires psutil library. (pip3 install psutil)
# Version 1.9.1
# Daniel Tate Wednesday 08-June-2022 3:35 PM
# Unlimited Modification Permitted
import argparse
import os
import getopt
import psutil
import sys
from time import perf_counter
from os.path import exists
from datetime import datetime
from datetime import timedelta

log_location = "/var/lib/portsentry"
log_prefix = "portsentry.blocked"
portsentry_exec = "portsentry"
differential_dir = "/tmp/portsentry_diff/"

isrunning: int = 0
diff=0
time: int = 0
warn=-1
crit=-1

def file_age (file, delta):
    cutoff = datetime.utcnow() - delta
    mtime = datetime.utcfromtimestamp(os.path.getmtime(file))
    if mtime < cutoff:
        return True
    return False

parser = argparse.ArgumentParser(description="Arguments")
parser.add_argument('-w', '--warn', help="Warning Threshold", type=int, metavar='warn')
parser.add_argument('-c', '--crit', help="Critical Threshold", type=int, metavar='crit')
parser.add_argument('-d', '--diff', help="differential, number of changes", type=int, metavar='int')
parser.add_argument('-t', '--time', help="Time in which to match elasticity")
args=parser.parse_args()

if __debug__:
    print(f"DEBUG: warn: {args.warn} crit: {args.crit} elastic thresh: {diff} elastic time: {time}")

if __debug__:
    print("DEBUG: individual crit: ", args.crit is None,"warn: ", args.warn is None)
    print("DEBUG: nested w/o diff", ((args.crit is None) or (args.warn is None)))
    print("DEBUG: nested w/ diff", (((args.crit is None) or (args.warn is None)) or diff is None))

if ((args.crit is None) or (args.warn is None)):
    if args.diff is not None:
        if __debug__: print(f"DEBUG: DECISION: debug flag set!")
        normal_mode = 0
    else:
        print("You must specify both warn and crit, or differential mode")
        normal_mode = 1
        exit(1)

elif args.warn > args.crit:
    print('warning level must be less than critical level')
    exit(2)


# Detect if we are in tcp or atcp mode.  
# This script does not check UDP

if __debug__: print(f"DEBUG: searching for {portsentry_exec} in psutil.process_iter()")
for process in psutil.process_iter():
    if process.name().startswith(portsentry_exec):
        if ("udp" in process.cmdline()):
            continue
        elif ("-atcp" in process.cmdline()):
            mode = "atcp"
            isrunning=1
            log = log_location + "/" + log_prefix + ".atcp"
            if not exists(log):
                print(f"CRITICAL: In atcp mode but logfile {log} not found!")
                exit (2)
            if __debug__:
                print("DEBUG: MAIN: ATCP mode:", mode, log)
                print(process.cmdline())
        elif ("-tcp" in process.cmdline()):
            log = log_location + "/" + log_prefix + ".tcp"
            if not exists(log):
                print(f"CRITICAL: In tcp mode but logfile {log} not found!")
                exit (2)
            isrunning=1
            mode="tcp"
            if __debug__:
                print("DEBUG: MAIN: ATCP Not Matched, mode:", mode, log)
                print(process.cmdline())

if __debug__:
    print(f"DEBUG: isrunning is set to {isrunning}")
    
status = os.system('systemctl is-active --quiet portsentry')
if (  status!=0  and  isrunning==0 ):
    print('CRITICAL Portsentry Service is not running!') 
    exit(2) 
# Detect if we are in differential mode.
if __debug__:print(f"DEBUG: args.diff is not None: {args.diff is not None}")
if args.diff is not None:
    if __debug__: print("DEBUG: Differential is ON")

    dir_exists = os.path.exists(differential_dir)
    if __debug__: print(f"DEBUG: DIFF: dir_exists: {dir_exists}")
    if not dir_exists:
        mkdir = os.makedirs(differential_dir)
        if __debug__: print("DEBUG: DIFF: mkdir: ",mkdir)

    with open(log,'r') as logfile:
        count = len(logfile.readlines())

    file_15m = open(differential_dir + "/15m", 'w')
    file_30m = open(differential_dir + "/30m", 'w')
    file_45m = open(differential_dir + "/45m", 'w')
    file_60m = open(differential_dir + "/60m", 'w')
    with open(differential_dir + "/00m", 'r') as f00m:
        str_assemble = str(perf_counter()),count
        #test = f00m.write(str(str_assemble))
        #print("DEBUG: DIF: Test is:", test)
        f00m.close()


### File Aging
if __debug__: print(f"DEBUG: AGING")
print("File 00m: ",file_age(differential_dir + "/00m",timedelta(minutes=15)))
if file_age(differential_dir + "/00m",timedelta(minutes=5)):
    print("DEBUG: DIFF: ROTATE: File 00m is 5 minutes old")

if __debug__:
    print("DEBUG: normal mode is:", normal_mode)
    print("DEBUG: normal logic test is:", (normal_mode == 1))
if (normal_mode == 1):
    with open(log,'r') as logfile:
        x = len(logfile.readlines())
        if __debug__: print(type(x), type(args.warn))
        if ( x < args.warn ):
            print('OK', x, "| bans=%d" %x)
            logfile.close()
            exit(0)

        elif ( x > args.warn and x < crit ):
            print('WARN', x,"| bans=%d" %x)
            logfile.close()
            exit(1)
        else:
            print('CRITICAL', x,"| bans=%d" %x)
            logfile.close()
            exit(2)
else:
    exit(1)