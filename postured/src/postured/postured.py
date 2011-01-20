#!/usr/bin/env python3

#from posturedrc import opts
from datetime import datetime, timedelta
from random import random
import imp
import sys
import os

def importpyfile(name, path):
    "Import a python module from path and call it name."
    try:
        return sys.modules[name]
    except KeyError:
        pass
    path = os.path.expanduser(path)
    with open(path, 'rb') as fp:
        return imp.load_module(name, fp, path, ('.py', 'rb', imp.PY_SOURCE))

# import our posturedrc file
# TODO: if we can't find it, we could always create it
importpyfile("posturedrc", "~/.posturedrc.py")
from posturedrc import opts


def weekdaystr(day):
    """
    Convert an int day to a string representation of the day.
    For example, 0 returns "Monday" and 6 returns "Sunday".  This
    mirrors the way datetime.weekday() works.
    """
    if day < 0 or day > 6:
        raise ValueError("day is out of range")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[day]

def tdtosecs(td):
    "Convert a timedelta to seconds."
    return (td.days * 24 * 60 * 60) + td.seconds + (td.microseconds * 0.000001)

def main():

    # time delta of zero
    tdzero = timedelta()

    # current time
    curdate = datetime.today()

    if opts.minlength > opts.maxlength:
        print("error: minlength cannot be greater than maxlength")

    if opts.minlength < tdzero: 
        print("error: minlength cannot be less than 0")

    if opts.maxlength < tdzero: 
        print("error: maxlength cannot be less than 0")

    difftime = opts.maxlength - opts.minlength

    print(difftime)

    print(tdtosecs(difftime))

    newsecs = tdtosecs(difftime) * random()
    newdelta = timedelta(seconds=newsecs) + opts.minlength

    print(newdelta)

    nexttime = datetime.today() + newdelta

    print("next alarm time: %s" % nexttime)

    ########

    if opts.starttime >= opts.endtime:
        print("Error: starttime is greater than or equal to endtime")

    curtime = curdate.time()
    print("curtime: " + str(curtime))

    if curtime < opts.starttime:
        print("curtime (" + str(curtime) + ") is before start time (" + str(opts.starttime) + ")")
        
    if curtime > opts.endtime:
        print("curtime (" + str(curtime) + ") is after end time (" + str(opts.endtime) + ")")


    if curdate.weekday() not in opts.days:
        print("current day (%s) is not in days (%s)" % 
                (weekdaystr(curdate.weekday()), [weekdaystr(day) for day in opts.days]))

    opts.action.run()



if __name__ == '__main__':
    main()