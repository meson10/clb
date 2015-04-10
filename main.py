#!/bin/python

from hosts import seed
from request import do

if __name__ == "__main__":
    seed([
        "http://search.yahoo.com/",
        "http://google.co.in",
        "http://amazon.com",
        "http://smnr.me"
    ])

    NUM = 15
    for x in xrange(NUM):
        print "============ Fetch: [%s] ============= " % x
        do()
