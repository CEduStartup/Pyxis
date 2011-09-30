import bjsonrpc
c = bjsonrpc.connect('localhost', 8000)
c1 = bjsonrpc.connect('localhost', 8001)

for i in range(1000):
    print c.call.get_trackers()
    print c1.call.test()


