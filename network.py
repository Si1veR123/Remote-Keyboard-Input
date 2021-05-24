import socket


class Network:
    def __init__(self):
        self.network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.network_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.local_machine_ip = socket.gethostbyname(socket.gethostname())
        self.port = 6700
