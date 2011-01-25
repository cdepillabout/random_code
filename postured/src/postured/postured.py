#!/usr/bin/env python2

from datetime import datetime, timedelta
from random import random
import imp
import sys, os, shutil
import argparse
import logging
import logging.handlers

logger = None

# this needs to be in here, otherwise importing actions from 
# the stock posturedrc doesn't work
from . import actions


def importconfig(rcfile=None):
    """
    Try to import ~/.posturedrc, and if we can't find it, 
    import posturedrc.py from within this module.
    """

    def importpyfile(name, path):
        "Import a python module from path and call it name."
        try:
            return sys.modules[name]
        except KeyError:
            pass
        path = os.path.expanduser(path)
        with open(path, 'rb') as fp:
            return imp.load_module(name, fp, path, ('.py', 'rb', imp.PY_SOURCE))

    if rcfile is None:
        rcfile = "~/.posturedrc"

    # when we import the file from the home directory, we don't want to
    # create bytecode and clutter up the user's $HOME
    __old_write_val = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    # import our posturedrc file, if we can't find it, we can just create it
    try:
        posturedrc_mod = importpyfile("postured.posturedrc", rcfile)
    except IOError as e:
        from . import posturedrc as sample_posturedrc
        if sample_posturedrc.__file__[-1] == "c":
            # this is a compiled python file, so we need to copy
            # over the uncompiled file
            shutil.copy(sample_posturedrc.__file__[:-1], os.path.expanduser(rcfile))
        else:
            shutil.copy(sample_posturedrc.__file__, os.path.expanduser(rcfile))
        posturedrc_mod = importpyfile("postured.posturedrc", rcfile)
    sys.dont_write_bytecode = __old_write_val

    return posturedrc_mod.opts


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

def calcsleepsecs(opts):
    "Calculate the number of seconds needed to sleep."

    minlength, maxlength, starttime, endtime, days, curdate, curtime = checksettings(opts)

    difftime = maxlength - minlength
    newsecs = tdtosecs(difftime) * random()
    newdelta = timedelta(seconds=newsecs) + minlength
    nexttime = datetime.today() + newdelta

    logger.debug("current time: " + str(curtime))
    logger.debug("next alarm time: %s" % nexttime)


def checksettings(opts):
    """
    Check that the settings values all make sense. Returns a tuple with
    minlength, maxlength, starttime, endtime, and days values from the 
    config file, and the curtime and curdate are sent back.
    """
    def assert_hasattr(opts, varname):
        if not hasattr(opts, varname):
            logger.error("No \"%s\" defined in config." % varname)
            sys.exit(1)
    assert_hasattr(opts, "minlength")
    assert_hasattr(opts, "maxlength")
    assert_hasattr(opts, "starttime")
    assert_hasattr(opts, "endtime")
    assert_hasattr(opts, "days")

    minlength = opts.minlength
    maxlength = opts.maxlength
    starttime = opts.starttime
    endtime = opts.endtime
    days = opts.days

    # current time
    curdate = datetime.today()

    # time delta of zero
    tdzero = timedelta()
    curtime = curdate.time()


    if minlength > maxlength:
        logger.error("minlength %s cannot be greater than maxlength %s" % (minlength, maxlength))
        sys.exit(1)

    if minlength < tdzero: 
        logger.error("minlength %s cannot be less than 0" % minlength)
        sys.exit(1)

    if maxlength < tdzero: 
        logger.error("maxlength %s cannot be less than 0" % maxlength)
        sys.exit(1)

    if starttime >= endtime:
        logger.error("starttime %s is greater than or equal to endtime %s" % 
                (starttime, endtime))
        sys.exit(1)

    if curtime < starttime:
        logger.error("curtime (" + str(curtime) + ") is before start time (" + str(starttime) + ")")
        sys.exit(1)
        
    if curtime > endtime:
        logger.error("curtime (" + str(curtime) + ") is after end time (" + str(endtime) + ")")
        sys.exit(1)

    if curdate.weekday() not in days:
        logger.error("current day (%s) is not in days (%s)" % 
                (weekdaystr(curdate.weekday()), [weekdaystr(day) for day in days]))
        sys.exit(1)

    return minlength, maxlength, starttime, endtime, days, curdate, curtime

def is_daemon(opts, args):
    """
    Checks if should daemonize or not.  Command line arguments override the
    args from the config file.
    """
    if args.daemonize == True:
        daemonize = True
    elif args.daemonize == False:
        daemonize = False
    else:
        if not hasattr(opts, "daemonize"):
            print >> sys.stderr, "No \"daemonize\" defined in config."
            sys.exit(1)
        else:
            daemonize = opts.daemonize
    return daemonize

def setuplogging(opts, daemonize):
    global logger

    # make sure loglevel is defined in the config
    if not hasattr(opts, "loglevel"):
        print >> sys.stderr, "No \"loglevel\" defined in config."
        sys.exit(1)

    logger = logging.getLogger()
    logger.setLevel(opts.loglevel)

    if daemonize:
        sysloghandler = logging.handlers.SysLogHandler("/dev/log", "daemon")
        formatter = logging.Formatter("postured[%(process)d]: %(levelname)s: %(message)s")
        sysloghandler.setFormatter(formatter)
        logger.addHandler(sysloghandler)
    else:
        class InfoHigherFilter(logging.Filter):
            def filter(self, rec):
                return rec.levelno <= logging.INFO
        class WarnLowerFilter(logging.Filter):
            def filter(self, rec):
                return rec.levelno >= logging.WARN

        stdouthandler = logging.StreamHandler(sys.stdout)
        stdouthandler.setLevel(logging.DEBUG)
        stdouthandler.addFilter(InfoHigherFilter())
        logger.addHandler(stdouthandler)

        stderrhandler = logging.StreamHandler(sys.stderr)
        stderrhandler.setLevel(logging.WARNING)
        stderrhandler.addFilter(WarnLowerFilter())
        logger.addHandler(stderrhandler)


def main():

    parser = argparse.ArgumentParser(description="A cron-like reminder daemon.")

    parser.add_argument('--rcfile', '-i', action='store', 
            help="rc file (something other than ~/.posturedrc)")
    parser.add_argument('--verbose', '-v', action='store_true', 
            help="detach from the controlling terminal")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--daemonize', '--daemon', '-D', dest="daemonize", 
            action='store_true', default=None, help="detach from the controlling terminal")
    group.add_argument('--no-daemonize', '--no-daemon', '-N', dest="daemonize", 
            action='store_false', default=None, help="detach from the controlling terminal")

    args = parser.parse_args()

    # try to import the config file the user wants to use
    if args.rcfile:
        opts = importconfig(rcfile)
    else:
        opts = importconfig()

    daemonize = is_daemon(opts, args)
    setuplogging(opts, daemonize)

    sleeptime = calcsleepsecs(opts)
    opts.action.run()

if __name__ == '__main__':
    main()
