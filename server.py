import socket

from time import sleep

from scapy.arch import get_if_addr


class Server:
    def __init__(self):
        self.ip_address = get_if_addr('eth1')
        self.player_names = ['', '']
        self.player_count = 0

        self.udp_thread = None

    def send_udp_offers(self):
        msg = bytes.fromhex('abcddcba02' + str(8888))
        while self.player_count < 2:
            print(f'Server started, listening on IP address {self.ip_address}')
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind((self.ip_address, 8888))
            sock.sendto(msg, ("255.255.255.255", 13117))
            sock.close()
            sleep(1)

    def tcp_client_connect(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.listen(2)
        clients = []
        while self.player_count < 2:
            try:
                client_socket, (client_ip, client_port) = tcp_socket.accept()
                clients.append([client_socket, (client_ip, client_port)])
                player_name = client_socket.recv(1024)
                self.player_names[self.player_count] = str(player_name)
                self.player_count += 1
            except Exception as e:
                print(f'Unable to connect to client.\n Exception received: {str(e)}')
        return clients

    def play_game(self):
        pass

    def run_server(self):
        pass


if __name__ == '__main__':
    server = Server()
    server.run_server()
