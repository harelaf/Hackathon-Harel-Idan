import socket
import threading
from style import style
from time import sleep
from scapy.arch import get_if_addr
import random
from struct import pack
import question_builder

class Server:
    def __init__(self, magic_cookie, message_type, server_port, client_port):
        self.MAGIC_COOKIE = magic_cookie
        self.MESSAGE_TYPE = message_type
        self.server_port = server_port
        self.client_port = client_port
        self.ip_address = get_if_addr('eth1')
        self.player_names = ['', '']
        self.client_answer = [-1, '']
        self.player_count = 0
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.tcp_socket.bind((self.ip_address, self.server_port))
        except socket.error as e:
            print(style.WARNING + f'Initialization of TCP SOCKET failed. Server initialization failed. Exiting...' + style.ENDC)
            exit()

    def send_udp_offers(self):
        """
        Summary: This function is used to send UDP offers in broadcast, every one second,
                 while there are less than 2 clients connected.
        """

        msg = pack('IbH', self.MAGIC_COOKIE, self.MESSAGE_TYPE, self.server_port)

        print(style.CYAN + f'Listening on IP address {self.ip_address}' + style.ENDC)
        while self.player_count < 2:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.bind((self.ip_address, 3332))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.sendto(msg, ("255.255.255.255", self.client_port))
            sock.close()
            sleep(1)

    def tcp_client_connect(self, clients):
        """
        Summary: This function is used to connect clients to the server using TCP.
                 The function accepts a client, waits a few seconds until it sends the team name, if the
                 client takes too long, we reject it.

        Args:
            clients (list of [socket, (ip, port)]): clients contains the sockets of the connected clients,
                                                    These are later used to send messages.
        """

        self.tcp_socket.listen()
        while self.player_count < 2:
            try:
                client_socket, (client_ip, client_port) = self.tcp_socket.accept()
                clients.append([client_socket, (client_ip, client_port)])
                client_socket.settimeout(3)
                try:
                    player_name = str(client_socket.recv(1024), 'utf8')
                except socket.error as e:
                    print(style.WARNING + f'Client: {client_ip} did not send team name in time.' + style.ENDC)
                    client_socket.close()
                    clients = clients[:-1]
                    continue
                self.player_names[self.player_count] = str(player_name)
                self.player_count += 1
                print(style.HEADER + f'{player_name}successfully connected to the server!' + style.ENDC)
            except Exception as e:
                print(style.WARNING + f'Unable to connect to client.\n Exception received: {str(e)}' + style.ENDC)

    def play_game(self, clients):
        """
        Summary: This function is used for the game logic.
                 We send the message to the clients simultaneously and then check which one was first to answer.
                 Then send the results to the clients.

        Args:
            clients (list of [socket, (ip, port)]): Using the tcp sockets to send messages.
        """

        ans, eq = question_builder.QuestionBuilder().get_question()
        msg = f'Welcome to Quick Maths.' \
              f'\nPlayer 1: {self.player_names[0]}' \
              f'\nPlayer 2: {self.player_names[1]}' \
              f'\n==' \
              f'\nPlease answer the following question as fast as you can:\n' \
              f'How much is {eq}?'
        clients[0][0].settimeout(10)
        clients[1][0].settimeout(10)

        clients[0][0].sendall(bytes(msg, 'utf8'))
        clients[1][0].sendall(bytes(msg, 'utf8'))

        mutex = threading.Lock()
        t1 = threading.Thread(target=self.get_answer, args=(clients[0][0], self.player_names[0], mutex))
        t2 = threading.Thread(target=self.get_answer, args=(clients[1][0], self.player_names[1], mutex))
        t1.start()
        t2.start()

        counter = 0
        while counter < 10 and self.client_answer == [-1, '']:
            counter += 1
            sleep(1)

        if self.client_answer == [-1, '']:
            msg = f"Game over!" \
                  f"\nThe correct answer was {ans}!" \
                  f"\nNo Winners - Ran out of time!"
        elif self.client_answer[0] == ans:
            msg = f"Game over!" \
                  f"\nThe correct answer was {ans}!" \
                  f"\nCongratulations to the winner: {self.client_answer[1]}"
        else:
            msg = f"Game over!" \
                  f"\nThe correct answer was {ans}!" \
                  f"\nCongratulations to the winner: {self.player_names[0] if self.player_names[1] == self.client_answer[1] else self.player_names[1]}"

        clients[0][0].send(bytes(msg, 'utf8'))
        clients[1][0].send(bytes(msg, 'utf8'))

    def get_answer(self, tcp_socket, team_name, mutex):
        """
        Summary: This function is used to parse the answer from the clients and pick the winner.

        Args:
            tcp_socket (socket): client socket
            team_name (string): name of team
        """

        client_ans = b''
        try:
            client_ans = tcp_socket.recv(1024)
            ans = int(client_ans)
        except ValueError as e:
            if len(client_ans) == 0:
                print(style.RED + f'{team_name} wasn\'t fast enough to answer!' + style.ENDC)
            else:
                print(style.RED + f'{team_name} didn\'t enter a digit!' + style.ENDC)
            return
        except socket.error as e:
            print(style.RED + f'{team_name} ran out of time!' + style.ENDC)
            return

        mutex.acquire()
        if self.client_answer[0] == -1:
            self.client_answer[0] = ans
            self.client_answer[1] = team_name
        mutex.release()

    def end_session(self):
        """
        Summary: This function is used to terminate the client, if the user is done.
        """

        val = input(style.GREEN + 'Terminate server? [Y\\N] ' + style.ENDC)
        if val == 'Y':
            self.tcp_socket.close()
            exit(0)

    def run_server(self):
        """
        Summary: This function is used to run all of the logic of the server.
        """

        print(style.CYAN + f'Server started successfully!' + style.ENDC)

        while True:
            clients = []
            t1 = threading.Thread(target=self.send_udp_offers)
            t2 = threading.Thread(target=self.tcp_client_connect, args=(clients,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            self.play_game(clients)

            self.client_answer = [-1, '']
            self.player_names = ['', '']
            self.player_count = 0

            # self.end_session()

            sleep(2)


if __name__ == '__main__':
    server = Server(magic_cookie=0xabcddcba, message_type=0x02, server_port=4567, client_port=13117)
    server.run_server()
