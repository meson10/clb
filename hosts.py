from datetime import datetime, timedelta
from itertools import cycle

from decorators import singleton

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


@singleton
class Hosts(object):
    """
    Hosts is a registry of all entries
    Seed() will seed the initial set of servers.
    Get() should do the magic of health checks and the right algorithm.
    """

    __slots__ = []

    snoozed = []
    __hosts__ = []
    registry = None
    MAX_RETRIES = 2
    SNOOZE = 3

    @classmethod
    def init_registry(cls):
        cls.registry = cycle(cls.__hosts__)

    @classmethod
    def seed(cls, hosts):
        if not isinstance(hosts, list):
            raise Exception("hosts must be an array to start with")

        cls.__hosts__ = [Host(addr) for addr in hosts]
        cls.init_registry()

    @classmethod
    def revive_snoozed(cls):
        DIRTY = False

        for host in cls.snoozed:
            if now() - host.last_used > timedelta(seconds=cls.SNOOZE):
                print "Enough sleep %s. Get back to Work" % host.address
                DIRTY = True
                host.is_busy = False
                cls.__hosts__.append(host)


        if DIRTY:
            cls.rearrange_servers()

    @classmethod
    def rearrange_servers(cls):
        new_hosts = []

        for host in cls.__hosts__:
            if host.is_busy:
                print "Host %s is busy. Marking it as snoozed." % (
                    host.address)

            elif host.retries >= cls.MAX_RETRIES - 1:
                print "Host %s failed far too often. Marking it as dead." % (
                    host.address)

                host.is_alive = False

            elif host.is_alive:
                new_hosts.append(host)

        cls.__hosts__ = new_hosts
        cls.init_registry()

    @classmethod
    def get(cls):
        if not cls.registry:
            raise AllHostsDown("Uh oh! All hosts are down.")

        cls.revive_snoozed()

        #Make this better. Use a proper method than just the next host.
        try:
            host = cls.registry.next()
        except StopIteration:
            raise AllHostsDown("Uh oh! All hosts are down.")

        if host.retries >= cls.MAX_RETRIES:
            cls.rearrange_servers()
            return cls.get()

        if host.is_busy:
            cls.snoozed.append(host)
            cls.rearrange_servers()
            return cls.get()

        host.mark_used()

        print "Electing %s from registry." % host
        return host


def seed(hosts):
    Hosts.seed(hosts)
