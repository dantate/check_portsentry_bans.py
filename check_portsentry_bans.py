#!/usr/bin/python3 -O
""" Description: check either current bans, or compare against the last 15-60m.
"""
# Super Basic check for portsentry service running and how many bans in atcp file
# Relies on portsentry being run by (or at least accessible to) systemd.
# Requires psutil library. (pip3 install psutil)
# Version 2.0.7b
# Daniel Tate Wednesday 08-June-2022 3:35 PM
# Unlimited Modification Permitted
#
# Excuse the mess - this was a learning exercise.

import argparse
import os
import psutil
import shutil
from time import perf_counter
from os.path import exists
from datetime import datetime
from datetime import timedelta

### User Variables

log_location = "/var/lib/portsentry"
log_prefix = "portsentry.blocked"
portsentry_exec = "portsentry"
tmp_dir = "/tmp/portsentry_diff/"

### Definitions

isrunning: int = 0
diff=0
time: int = 0
warn=-1
crit=-1
differential_dir = tmp_dir + "/"
new_bans=0
aged_bans=0


def file_age (file, delta):
    cutoff = datetime.utcnow() - delta
    mtime = datetime.utcfromtimestamp(os.path.getmtime(file))
    if mtime < cutoff:
        return True
    return False

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def get_aged_bans (difffile):
    if __debug__: print("DEBUG: SUB: get_aged_bans")
    with open(difffile, 'r') as dfile:
        lines = dfile.readlines()
        for line in lines:
            my_list=line.split()
            bancount=my_list[1]
            if __debug__:
                print("DEBUG: SUB: aged_bans: my_list: ",my_list)
                print("DEBUG: SUB: aged_bans: bancount: ",bancount)
            dfile.close()
            return bancount

def rotate ():
        if __debug__: print(f"DEBUG: DIFF: ROTATE: File 00m is {args.time} minutes old")
        os.replace(differential_dir + "45m", differential_dir + "60m")
        os.replace(differential_dir + "30m", differential_dir + "45m")
        os.replace(differential_dir + "15m", differential_dir + "30m")
        os.replace(differential_dir + "00m", differential_dir + "15m")
        if __debug__: print("DEBUG: DIFF: POSTROTATE: Creating new datafile...")
        with open(differential_dir + "00m", 'w') as f00m:
            str_assemble1 = str(perf_counter())
            str_assemble2 = str(str(count))
            str_assemble = str_assemble1 + " " + str_assemble2
            test = f00m.write(str_assemble)
            if __debug__: print("DEBUG: DIFF: POSTROTATE: New Create is:", test)
            f00m.close()

def setup_env ():
    mkdir = os.makedirs(differential_dir)
    if __debug__:
        print("DEBUG: DIFF: mkdir: ", mkdir)
        print("DEBUG: DIFF: Creating initial file")
    with open(differential_dir + "00m", 'w') as f00m:
        str_assemble1 = str(perf_counter())
        str_assemble2 = str(str(count))
        str_assemble = str_assemble1 + " " + str_assemble2
        write = f00m.write(str(str_assemble))
        if __debug__: print("DEBUG: DIFF: write is", write)
        f00m.close()
        shutil.copy(differential_dir + "00m", differential_dir + "15m")
        shutil.copy(differential_dir + "00m", differential_dir + "30m")
        shutil.copy(differential_dir + "00m", differential_dir + "45m")
        shutil.copy(differential_dir + "00m", differential_dir + "60m")

def validate_differential ():
    if int(aged_bans) == count:
        if __debug__:
            print(f"OK: Bans Unchanged {int(aged_bans)} == {count}|count={count}")
            exit(0)
        else:
            print(f"OK: Bans Unchanged {int(aged_bans)}|bans={aged_bans};{args.warn};{args.crit}")
            exit(0)
    elif int(aged_bans) > count:
        if __debug__:
            print(f"OK: Decrease in bans {int(aged_bans)} > {count}")
            exit(0)
        else:
            print(f"OK: Decrease in bans from {int(aged_bans)} to {count} |bans={count};{args.warn};{args.crit}")
            exit(0)
    elif (new_bans < args.warn):
        if __debug__:
            print(f"OK: {new_bans} new in {args.time} is less than {args.warn} new in {args.time}")
            exit(0)
        else:
            print(f"OK: {new_bans} new bans in {args.time}|bans={new_bans};{args.warn};{args.crit}")
            exit(0)
    elif (new_bans >= args.warn and new_bans < args.crit):
        if __debug__:
            print( f"WARNING: {new_bans} new in {args.time} is greater than or equal to warn: {args.warn} new in {args.time}")
            exit(1)
        else:
            print(f"WARNING: {new_bans} new in {args.time}|bans={new_bans};{args.warn};{args.crit}")
            exit(1)
    else:
        if __debug__:
            print(f"CRITICAL: bans: {new_bans} new in {args.time} is greater than crit: {args.crit} new in {args.time}")
            exit(2)
        else:
            print(f"CRITICAL: bans: {new_bans} new bans in in {args.time}|bans={new_bans};{args.warn};{args.crit}")
            exit(2)

def validate_normal ():
    with open(log,'r') as logfile:
        x = len(logfile.readlines())
        if __debug__: print(type(x), type(args.warn))
        if ( x < args.warn ):
            print('OK', x, "| bans=%d" %x)
            logfile.close()
            exit(0)

        elif ( x >= args.warn and x < args.crit ):
            print('WARN', x,"| bans=%d" %x)
            logfile.close()
            exit(1)
        else:
            print('CRITICAL', x,"| bans=%d" %x)
            logfile.close()
            exit(2)

### Get Parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--diff', help="Differential mode", action='store_true')
parser.add_argument('-t', '--time', help="Minutes for differential", type=int, metavar='15,30,45,60')
parser.add_argument('-w', '--warn', help="Warning Threshold", type=int, metavar='warn')
parser.add_argument('-c', '--crit', help="Critical Threshold", type=int, metavar='crit')
args=parser.parse_args()


if __debug__:
    print(f"DEBUG: warn: {args.warn} crit: {args.crit} elastic thresh: {args.diff} elastic time: \
{args.time}")

if __debug__:
    print("DEBUG: individual NONEs crit: ", args.crit is None,"warn: ", args.warn is None, "diff", args.diff is None)
    print("DEBUG: nested w/o diff", ((args.crit is None) or (args.warn is None)))
    print("DEBUG: nested w/ diff", (((args.crit is None) or (args.warn is None)) or diff is None))
    print(f"DEBUG: check_param: crit {args.crit} warn {args.warn} diff {args.diff}")

### Determine flags..

if (args.crit is not None) and (args.warn is not None):
    if __debug__: print(f"DEBUG: passed crit/warn validation")
    if args.diff is True:
        if __debug__: print(f"DEBUG: args.diff is True")
        normal_mode = 0
        if __debug__: print("DEBUG: str test for time: ",str(args.time) in {"15", "30", "45", "60"})
        if str(args.time) in {"15", "30", "45", "60"}:
            if __debug__: print("DEBUG: Time Matched")
        else:
            if __debug__: print("DEBUG: Time NOT Matched")
            print(f"You must specify 15, 30, 45, or 60 minutes as the time window.")
            exit(1)
    else:
        if __debug__: print(f"DEBUG: args.diff is False, falling to normal mode")
        normal_mode = 1

if (args.diff and not args.time):
    print("You must specify time with differential.")
    exit(1)

if (args.time and not args.diff):
    print("You must specify differential with time.")

elif (args.crit is None) or (args.warn) is None:
  print(f"ERROR: you must specify crit and warn")
  exit(2)
elif (args.crit == args.warn):
    print(f"ERROR: warn and crit must be different values")
    exit(2)
elif args.warn > args.crit:
    print('warning level must be less than critical level')
    exit(2)


# Detect if we are in tcp or atcp mode and get current bans.
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

with open(log, 'r') as logfile:
    count = len(logfile.readlines())
    if __debug__: print(f"DEBUG: got {count} current bans from logfile!")

if __debug__:
    print(f"DEBUG: isrunning is set to {isrunning}")
    
status = os.system('systemctl is-active --quiet portsentry')
if (  status!=0  and  isrunning==0 ):
    print('CRITICAL Portsentry Service is not running!') 
    exit(2) 
# Detect if we are in differential mode.
if __debug__:print(f"DEBUG: DIFF: args.diff is True: {args.diff is True}")
if args.diff is True:
    if __debug__: print("DEBUG: DIFF: Differential is ON")

### Do Setup if Needed.

    dir_exists = os.path.exists(differential_dir)
    if __debug__: print(f"DEBUG: DIFF: dir_exists: {dir_exists}")
    if not dir_exists:
        setup_env()

if __debug__:
    print("DEBUG: normal mode is:", normal_mode)
    print("DEBUG: normal logic test is:", (normal_mode == 1))

### File Aging
if (normal_mode == 0):

    if __debug__:
        print(f"DEBUG: DIFF: DIFFERENTIAL")
        print(f"DEBUG: Aging...")
        print("DEBUG: DIFF: ROTATE: File 00m: ",file_age(differential_dir + "00m",timedelta(minutes=args.time)))
    if file_age(differential_dir + "00m",timedelta(minutes=args.time)):
        aged_bans = get_aged_bans(differential_dir + str(args.time) +"m")
        new_bans = (count - int(aged_bans))
        rotate()
        validate_differential()

    else:
        if __debug__: print("DEBUG: DIFF: NOAGE: File is not yet aged out.")
        aged_bans = get_aged_bans(differential_dir + str(args.time) +"m")
        new_bans = (count - int(aged_bans))
        validate_differential()

if (normal_mode == 1):
    if __debug__: print(f"In NORMAL MODE {normal_mode}")
    validate_normal()

else:
    exit(1)