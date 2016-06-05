# coding=utf-8

from datetime import datetime, timedelta
from time import mktime


def checkpoints():

    t0 = datetime.strptime('2014-07-09 11', '%Y-%m-%d %H')
    hours_per_cycle = 175

    t = datetime.now()

    seconds = mktime(t.timetuple()) - mktime(t0.timetuple())
    cycles = seconds // (3600 * hours_per_cycle)
    start = t0 + timedelta(hours=cycles * hours_per_cycle)
    checkpoints = map(lambda x: start + timedelta(hours=x), range(0, hours_per_cycle, 5))

    for num, checkpoint in enumerate(checkpoints):
        print '%02d %s' % (num, checkpoint)

if __name__ == '__main__':
    checkpoints()
