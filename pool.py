import multiprocessing
from urllib3 import (
    connection_from_url,
    HTTPConnectionPool
)

from decorators import singleton
from hosts import Hosts


def get_pool_size():
    #Set POOL SIZE as twice of the CPU_COUNT.
    #2 per core sounds like a fair number.
    return 2 * multiprocessing.cpu_count()


class EachPool(object):
    __slots__ = ["host", "pool"]

    def __init__(self, host, pool):
        self.host = host
        self.pool = pool

    def is_server_busy(self, req):
        #Read Headers here to mark server as busy.
        if "yahoo.com" in self.host.address:
            return True

        return False

    def request(self, *args, **kwargs):
        #Just a proxy to self.pool.request
        #No wait, it has started doing a lot more.

        try:
            req = self.pool.request(*args, **kwargs)
            if self.is_server_busy(req):
                print "Host %s being marked as busy" % (self.host.address)
                self.host.mark_busy()

            return req

        except Exception, e:
            print "Host %s failed for reason %s" % (
                self.host.address, str(e))

            self.host.mark_failure(e)
            raise e


@singleton
class ConnectionPool(object):
    """
    Based on the urllib3 connection pool document available at:
    https://urllib3.readthedocs.org/en/latest/pools.html
    """

    __slots__ = ["CACHE"]

    CACHE = {}

    @classmethod
    def get(cls):
        #Fetch the next host to be queried. Hide this logic from pool.
        host = Hosts.get()
        address = host.address

        pool = cls.CACHE.get(address)
        #Look for the Pool if it is already cached.
        if not pool:
            #Cached value is missing. Allocate a new Pool.

            print "Seeding a new Connection pool for Host %s" % address

            pool = EachPool(
                host,
                connection_from_url(address, maxsize=get_pool_size()))

            cls.CACHE[address] = pool

        return pool

