import socket
import threading
from style import style
from time import sleep, time
from scapy.arch import get_if_addr
import random

class Server:
    def __init__(self):
        self.ip_address = get_if_addr('eth1')
        self.player_names = ['', '']
        self.player_count = 0
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.tcp_socket.bind((self.ip_address, 4567))
        self.client_answer = [-1, '']

    def send_udp_offers(self):
        msg = bytes.fromhex('abcddcba02' + str(4567))
        print(f'Server started, listening on IP address {self.ip_address}')
        while self.player_count < 2:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.bind((self.ip_address, 3332))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.sendto(msg, ("255.255.255.255", 13117))
            sock.close()
            sleep(1)

    def tcp_client_connect(self, clients):
        self.tcp_socket.listen()
        while self.player_count < 2:
            try:
                client_socket, (client_ip, client_port) = self.tcp_socket.accept()
                clients.append([client_socket, (client_ip, client_port)])
                client_socket.settimeout(3)
                try:
                    player_name = str(client_socket.recv(1024), 'utf8')
                except socket.error as e:
                    print(f'Client: {client_ip} did not send team name in time.')
                    continue
                client_socket.settimeout(10)
                self.player_names[self.player_count] = str(player_name)
                self.player_count += 1
            except Exception as e:
                print(f'Unable to connect to client.\n Exception received: {str(e)}')

    def play_game(self, clients):
        ans, eq = self.question_bank()
        msg = f'Welcome to Quick Maths.' \
              f'\nPlayer 1: {self.player_names[0]}' \
              f'\nPlayer 2: {self.player_names[1]}' \
              f'\n==' \
              f'\nPlease answer the following question as fast as you can:\n' \
              f'How much is {eq}?'
        clients[0][0].sendall(bytes(msg, 'utf8'))
        clients[1][0].sendall(bytes(msg, 'utf8'))

        t1 = threading.Thread(target=self.get_answer, args=(clients[0][0], self.player_names[0]))
        t2 = threading.Thread(target=self.get_answer, args=(clients[1][0], self.player_names[1]))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

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

        self.client_answer = [-1, '']
        self.player_names = ['', '']
        self.player_count = 0

    def get_answer(self, tcp_socket, team_name):
        try:
            ans = int(tcp_socket.recv(1024))
        except socket.error as e:
            print(f'{team_name} ran out of time')
            return
        mutex = threading.Lock()
        mutex.acquire()
        if self.client_answer[0] == -1:
            self.client_answer[0] = ans
            self.client_answer[1] = team_name
        mutex.release()

    def question_bank(self):
        operator_functions = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
        }
        ans = ''
        eq = ''
        while len(str(ans)) != 1:
            first_number = random.choice(range(0, 16))
            op1, op_func1 = random.choice(list(operator_functions.items()))
            second_number = random.choice(range(0, 16))
            op2, op_func2 = random.choice(list(operator_functions.items()))
            third_number = random.choice(range(0, 16))
            try:
                if op1 == '/' or op1 == '*':
                    ans = op_func2(op_func1(first_number, second_number), third_number)
                    eq = f'({first_number} {op1} {second_number}) {op2} {third_number}'
                elif op2 == '/' or op2 == '*':
                    ans = op_func1(first_number, op_func2(second_number, third_number))
                    eq = f'{first_number} {op1} ({second_number} {op2} {third_number})'
                else:
                    ans = op_func2(op_func1(first_number, second_number), third_number)
                    eq = f'{first_number} {op1} {second_number} {op2} {third_number}'
            except ZeroDivisionError:
                continue
        return ans, eq

    def run_server(self):
        while True:
            clients = []
            t1 = threading.Thread(target=self.send_udp_offers)
            t2 = threading.Thread(target=self.tcp_client_connect, args=(clients,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            self.play_game(clients)


if __name__ == '__main__':
    server = Server()
    server.run_server()
