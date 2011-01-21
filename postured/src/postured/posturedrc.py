import datetime
import os
import postured.actions

class Options(object):
    minlength = datetime.timedelta(minutes=30)
    maxlength = datetime.timedelta(hours=2)

    starttime = datetime.time(hour=9)  # 11 am
    endtime = datetime.time(hour=11)    # 7 pm

    # days of the week (monday is 0 and sunday is 6)
    days = [0, 1, 2, 3, 4]              # M, Tu, W, Th, F 

    action = postured.actions.PlaySound()


opts = Options()

