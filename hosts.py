from datetime import datetime
from itertools import cycle

from decorators import singleton

class Host(object):
    """
    Single Host entry. Starts with 0 load and is_alive=True.
    Ideally all is_alive=False should be cleaned up from the registry.
    """

    __slots__ = ["address", "load", "is_alive", "last_used", "retries"]

    def __str__(self):
        return "Address: %s Alive: %s Retries: %s" % (
            self.address, self.is_alive, self.retries)

    def __init__(self, address):
        self.address = address

        self.load = 0
        self.retries = 0
        self.is_alive = True
        self.last_used = None


    def reset(self):
        self.is_alive = True
        self.retries = 0


    def mark_dead(self):
        self.is_alive = False


    def mark_used(self):
        self.last_used = datetime.now()


    def mark_failure(self, reason=None):
        self.retries += 1


@singleton
class Hosts(object):
    """
    Hosts is a registry of all entries
    Seed() will seed the initial set of servers.
    Get() should do the magic of health checks and the right algorithm.
    """

    __slots__ = ["registry", "MAX_RETRIES", "__hosts__"]

    __hosts__ = []
    registry = None
    MAX_RETRIES = 2

    @classmethod
    def seed(cls, hosts):
        if not isinstance(hosts, list):
            raise Exception("hosts must be an array to start with")

        cls.__hosts__ = [Host(addr) for addr in hosts]
        cls.registry = cycle(cls.__hosts__)

    @classmethod
    def rearrange_servers(cls):
        new_hosts = []

        for host in cls.__hosts__:
            if host.retries >= cls.MAX_RETRIES:
                print "Host %s failed far too often. Marking it as dead." % (
                    host.address)

                host.is_alive = False

            if host.is_alive:
                new_hosts.append(host)

        cls.registry = cycle(cls.__hosts__)

    @classmethod
    def get(cls):
        if not cls.registry:
            raise Exception("Uh oh! All hosts are down.")

        #Make this better. Use a proper method than just the next host.
        host = cls.registry.next()

        if host.retries >= cls.MAX_RETRIES:
            cls.rearrange_servers()
            return cls.get()

        host.mark_used()

        print "Electing %s from registry." % host
        return host


def seed(hosts):
    Hosts.seed(hosts)
