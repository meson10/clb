#!/bin/python

from lib import make_clb

if __name__ == "__main__":
    yahoo_urls = ["/yahoo1", "/yahoo2", "/yahoo3"]
    google_urls = ["/google1", "/google2", "/google3"]
    smnr_urls = ["/siminar1", "/siminar2", "/siminar3"]

    yahoo_hosts = [
        "http://search.yahoo.com/",
        "http://search.yahoo.co.in/",
    ]

    google_hosts = [
        "http://www.google.co.in",
        "http://www.google.com"
    ]

    smnr_hosts = [
        "http://smnr.me",
        "http://staging.smnr.me"
    ]

    yahoo_clb = make_clb(yahoo_hosts)
    google_clb = make_clb(google_hosts)
    siminar_clb = make_clb(smnr_hosts)

    for url in yahoo_urls:
        yahoo_clb.get(url)

    for url in google_hosts:
        google_clb.get(url)

    for url in smnr_urls:
        siminar_clb.get(url)
