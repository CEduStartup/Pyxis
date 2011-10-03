import bjsonrpc
c = bjsonrpc.connect('localhost', 8001)

for i in range(10000):
    print c.call.test()
