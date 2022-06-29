# check_portsentry_bans.py
icinga2 check portsentry bans

Checks the number of bans portsentry has recorded since startup.  Works for tcp or atcp mode.  Tested with iCinga2 and iCingaWeb2.
Untested with Nagios but should work just the same.

branch: differential_dev contains code that will measure the differential from one time period to another, but is pre-release.
