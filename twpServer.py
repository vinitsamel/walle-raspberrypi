import socket
import sys
import string

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address given on the command line
server_name = sys.argv[1]
server_address = (server_name, 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.listen(1)

while True:
    print ('waiting for a connection...')
    connection, client_address = sock.accept()
    try:
        print >>sys.stderr, 'client connected:', client_address
        data = ""
        while True:
        	#print >>sys.stderr,'Bdata = ', data
        	data = data + connection.recv(64)
        	#print >>sys.stderr,'Adata = ', data
        	# Split on delimiter to print complete message
        	dataArr = string.split(data, '|')
        	for x in range(0, len(dataArr) - 1 ):
        		print dataArr[x]
        	if len(dataArr) >= 1:
        		data = dataArr[-1]
    finally:
        connection.close()