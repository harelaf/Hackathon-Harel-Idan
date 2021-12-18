from socket import *
import socket


class Client:

    def __init__(self):
        self.port = 13117
        self.server_ip = None
        self.server_port = None

        self.MAGIC_COOKIE = "abcddcba"
        self.MESSAGE_TYPE = "02"

    def look_for_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind(('', self.port))

        while True:
            data, addr = sock.recvfrom(1024)
            self.server_ip = addr[0]
            data_hex = data.hex()
            if data_hex[:8] != self.MAGIC_COOKIE:
                continue
            if data_hex[8:10] != self.MESSAGE_TYPE:
                continue
            self.server_port = data_hex[10:]

c = Client()
c.look_for_server()

