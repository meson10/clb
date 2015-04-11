from datetime import datetime, timedelta
from itertools import cycle

#from decorators import singleton

def now():
    return datetime.now()


class AllHostsDown(Exception):
    pass

class Host(object):
    """
    Single Host entry. Starts with 0 load and is_alive=True.
    Ideally all is_alive=False should be cleaned up from the registry.
    """

    __slots__ = ["address", "load", "is_alive", "last_used", "retries", "is_busy"]

    def __str__(self):
        return "Address: %s Alive: %s Retries: %s" % (
            self.address, self.is_alive, self.retries)

    def __init__(self, address):
        self.address = address

        self.load = 0
        self.retries = 0
        self.is_busy = False
        self.is_alive = True
        self.last_used = None


    def mark_busy(self):
        self.is_busy = True

    def reset(self):
        self.is_alive = True
        self.retries = 0


    def mark_dead(self):
        self.is_alive = False


    def mark_used(self):
        self.last_used = now()


    def mark_failure(self, reason=None):
        self.retries += 1

class Hosts(object):
    """
    Hosts is a registry of all entries
    Seed() will seed the initial set of servers.
    Get() should do the magic of health checks and the right algorithm.
    """

    __slots__ = ["__hosts__", "snoozed", "registry"]

    MAX_RETRIES = 2
    SNOOZE = 300

    def init_registry(self):
        self.registry = cycle(self.__hosts__)

    def __init__(self, hosts):
        if not isinstance(hosts, list):
            raise Exception("hosts must be an array to start with")

        self.__hosts__ = [Host(addr) for addr in hosts]
        self.snoozed = []
        self.registry = None
        self.init_registry()

    def revive_snoozed(self):
        DIRTY = False

        for host in self.snoozed:
            if now() - host.last_used > timedelta(seconds=self.SNOOZE):
                print "Enough sleep %s. Get back to Work" % host.address
                DIRTY = True
                host.is_busy = False
                self.__hosts__.append(host)
                self.snoozed.pop()


        if DIRTY:
            self.rearrange_servers()

    def rearrange_servers(self):
        new_hosts = []

        for host in self.__hosts__:
            if host.is_busy:
                print "Host %s is busy. Marking it as snoozed." % (
                    host.address)

            elif host.retries >= self.MAX_RETRIES:
                print "Host %s failed far too often. Marking it as dead." % (
                    host.address)

                host.is_alive = False

            elif host.is_alive:
                new_hosts.append(host)

        self.__hosts__ = new_hosts
        self.init_registry()

    def get(self):
        if not self.registry:
            raise AllHostsDown("Uh oh! All hosts are down.")

        self.revive_snoozed()

        #Make this better. Use a proper method than just the next host.
        try:
            host = self.registry.next()
        except StopIteration:
            raise AllHostsDown("Uh oh! All hosts are down.")

        if host.retries >= self.MAX_RETRIES:
            self.rearrange_servers()
            return self.get()

        if host.is_busy:
            self.snoozed.append(host)
            self.rearrange_servers()
            return self.get()

        host.mark_used()

        print "Electing %s from registry." % host
        return host
