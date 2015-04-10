#!/bin/python

from hosts import seed
from request import do


if __name__ == "__main__":
    seed([
        "http://yahoo.com/",
        "http://google.co.in",
        "http://amazon.com"
    ])

    do()
