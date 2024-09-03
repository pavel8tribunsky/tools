# encoding UTF-8
# dependencies: socket

import socket

socket.setdefaulttimeout(1)
host = socket.gethostbyname(socket.gethostname())

#print(host)
#print(socket.gethostname())
#print(socket.getfqdn())

print(socket.gethostbyaddr('192.168.20.189'))
print(socket.getfqdn('192.168.20.189'))

#local_net = host.split(".")
#local_net = local_net[:3]
#local_net = ".".join(local_net)

#for addr in range(1, 255):
#    l_net = ".".join((local_net, str(addr)))
#    # print("IP:", l_net, "Name:", print(socket.getfqdn(l_net)))
#    try:
#        print("IP:", l_net, "Name:", print(socket.gethostbyaddr(l_net)))
#    except socket.herror:
#        pass
