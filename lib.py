from pool import ConnectionPool
from hosts import Hosts


def make_clb(hosts):
    host_manager = Hosts(hosts)
    pool = ConnectionPool(host_manager)
    return pool
