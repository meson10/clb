import multiprocessing
from functools import partial
from decorators import singleton

from urllib3 import (
    connection_from_url,
    HTTPConnectionPool
)

#from hosts import Hosts
#Not needed anymore. Passed around as a constructor argument to Pool.


def get_pool_size():
    #Set POOL SIZE as twice of the CPU_COUNT.
    #2 per core sounds like a fair number.
    return 2 * multiprocessing.cpu_count()


class ConnectionPool(object):
    MAX_RETRIES = 5

    __slots__ = ["host_manager", "get", "put", "post", "delete", "options"]

    def __init__(self, host_manager):
        self.host_manager = host_manager

        for method in ["get", "put", "post", "delete", "options"]:
            #TOOD: Plese validate syntax later.
            setattr(self, method, partial(self.do, method=method.title()))

    def is_server_busy(self, req, host):
        #Read Headers here to mark server as busy.
        if "yahoo.com" in host.address:
            return True

        return False

    def request(self, *args, **kwargs):
        #Just a proxy to self.pool.request
        #No wait, it has started doing a lot more.

        #Fetch the next host to be queried. Hide this logic from pool.
        try:
            host = self.host_manager.get()
        except Exception, e:
            print e
            return

        pool = EachPool.get(host)

        try:
            req = pool.request(*args, **kwargs)
            if self.is_server_busy(req, host):
                print "Host %s being marked as busy" % (host.address)
                host.mark_busy()

            return req

        except Exception, e:
            print "Host %s failed for reason %s" % (
                host.address, str(e))

            host.mark_failure(e)
            raise e

    def do(self, url, method="GET"):
        """
        Underlying method to fetch data.
        Method to perform the actual request.
        """

        i = 0

        while i < self.MAX_RETRIES:
            print "======== Fetch: [%s] Attempt: [%s] =========" % (url, i)
            i += 1

            try:
                r = self.request(method, url)
                return r
            except Exception, e:
                print "Retrying..."


@singleton
class EachPool(object):
    """
    Based on the urllib3 connection pool document available at:
    https://urllib3.readthedocs.org/en/latest/pools.html
    """

    __slots__ = []
    CACHE = {}

    @classmethod
    def get(self, host):
        address = host.address

        pool = self.CACHE.get(address)
        #Look for the Pool if it is already cached.
        if not pool:
            #Cached value is missing. Allocate a new Pool.

            print "Seeding a new Connection pool for Host %s" % address

            pool = connection_from_url(address, maxsize=get_pool_size())

            self.CACHE[address] = pool

        return pool

