#!/usr/bin/python3 -O
# Super Basic check for portsentry service running and how many bans in atcp file
# Version 1.2 
# Daniel Tate Wednesday 08-June-2022 3:35 PM
# Unlimited Modification Permitted

import os 
import getopt
import psutil
import sys

log_location = "/var/lib/portsentry"


def command_line_validate(argv):
  try:
    opts, args = getopt.getopt(argv, 'w:c:o:', ['warn=' ,'crit='])
  except getopt.GetoptError:
    print(usage)
  try:
    for opt, arg in opts:
      if opt in ('-w', '--warn'):
        try:
          warn = int(arg)
        except:
          print('Warn value must be an int')
          exit(2)
      elif opt in ('-c', '--crit'):
        try:
          crit = int(arg)
        except:
          print('crit value must be an int')
          exit(2)
      else:
        print(usage)
    try:
      isinstance(warn, int)
      #print('warn level:', warn
    except:
      print('warn level is required')
      print(usage)
      exit(2)
    try:
      isinstance(crit, int)
    except:
      print('crit level is required')
      print(usage)
      exit(2)
  except:
    exit(2)
  # confirm that warning level is less than 2 level, alert and exit if check fails
  if warn > crit:
    print('warning level must be less than 2 level***')
    exit(2)
  return warn, crit

#def main():
argv=sys.argv[1:]
warn, crit = command_line_validate(argv)

if __debug__:
    print('Debug ON')
    print('args: ', warn, crit)

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
    print('2 Portsentry Service is not running!') 
    exit(2) 

with open(log,'r') as tcp:
    x = len(tcp.readlines())
    if ( x < warn ):
        print('OK', x, "| bans=%d" %x)
        tcp.close()
        exit(0)
    
    elif ( x > warn and x < crit ):
        print('WARN', x,"| bans=%d" %x)
        tcp.close()
        exit(1)
    else:
        print('CRITICAL', x,"| bans=%d" %x)
        tcp.close()
        exit(2)
