import socket


class Client:

    def __init__(self):
        self.server_ip = None
        self.server_port = None
        self.tcp_socket = None

        self.TEAM_NAME = "Big Shaq"
        self.MAGIC_COOKIE = "abcddcba"
        self.MESSAGE_TYPE = "02"

    def look_for_server(self):
        print("Client started, listening for offer requests...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # USE THIS ON LINUX
        sock.bind(('', 13117))

        while True:
            data, addr = sock.recvfrom(1024)
            data_hex = data.hex()
            if data_hex[:8] != self.MAGIC_COOKIE:
                # print("Failed to connect to server: UDP packet didn't contain 0xabcddcba in MAGIC COOKIE field.")
                continue
            if data_hex[8:10] != self.MESSAGE_TYPE:
                # print("Failed to connect to server: UDP packet didn't contain 0x02 in MESSAGE TYPE field.")
                continue
            self.server_ip = addr[0]
            print(self.server_ip)
            self.server_port = int(data_hex[10:])
            print(self.server_ip, self.server_port)
            sock.close()
            break

    def connect_to_server(self):
        print(f'Received offer from {self.server_ip}, attempting to connect...')
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.tcp_socket.settimeout(3)

        try:
            self.tcp_socket.connect((self.server_ip, self.server_port))
        except socket.error as e:
            print(f'Failed to connect to server: timed out while connecting with TCP.\nException thrown: {str(e)}')
            return False

        print(f'Successfully connected to server {self.server_ip}')
        team_name_as_bytes = bytes(self.TEAM_NAME + '\n', 'utf8')
        self.tcp_socket.sendall(team_name_as_bytes)
        self.tcp_socket.settimeout(None)
        return True

    def get_msg_from_server(self):
        server_msg = str(self.tcp_socket.recv(1024), 'utf8')
        print(server_msg)

    def send_client_answer(self):
        ans = input('Please enter the answer to the math problem: ')[0]
        self.tcp_socket.send(bytes(ans, 'utf8'))

    def run_client(self):
        while True:
            self.look_for_server()
            success = self.connect_to_server()
            if not success:
                continue
            self.get_msg_from_server()  # Get welcome message and math problem
            self.send_client_answer()   # Send answer to server
            self.get_msg_from_server()  # Get game results
            # GET BACK TO LISTENING TO OFFERS


if __name__ == '__main__':
    client = Client()
    client.run_client()
