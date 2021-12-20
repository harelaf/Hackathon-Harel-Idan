from socket import *
import socket
from time import sleep

class Server:
    def __init__(self):
        self.MAGIC_COOKIE = "abcddcba"
        self.MESSAGE_TYPE = "02"

    def broadcasting(self):

        interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        allips = [ip[-1][0] for ip in interfaces]
        msg = bytes.fromhex('abcddcba020001')
        while True:

            for ip in allips:
                print(f'sending on {ip}')
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind((ip, 0))
                sock.sendto(msg, ("255.255.255.255", 13117))
                sock.close()

            sleep(2)

s = Server()
s.broadcasting()
# msg = bytes.fromhex('abcddcba020001')
# d = msg.hex()
# print(d)