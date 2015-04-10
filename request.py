from pool import ConnectionPool

def enable_keep_alive(pool):
    # HTTPConnection.default_socket_options + [
    # (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
    # ]

    pass

def do():
    """
    Method to perform the actual request.
    """

    NUM = 15
    MAX_RETRIES = 15

    for x in xrange(NUM):
        print "============ Fetch: [%s] ============= " % x

        i = 0
        while i < xrange(MAX_RETRIES):
            pool = ConnectionPool.get()
            try:
                r = pool.request("GET", "/hello")
            except Exception, e:
                print "Retrying..."
            else:
                break
