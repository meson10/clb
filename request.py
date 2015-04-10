from pool import Pool

def enable_keep_alive(pool):
    # HTTPConnection.default_socket_options + [
    # (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
    # ]

    pass

def do():
    """
    Method to perform the actual request.
    """

    NUM = 5
    MAX_RETRIES = 5

    for x in xrange(NUM):
        i = 0

        while i < xrange(MAX_RETRIES):
            pool = Pool.get()
            try:
                r = pool.request("GET", "/hello")
            except Exception, e:
                print "Retrying"
            else:
                break
