import socket

from socket_messenger.network.client_connection import ClientConnection

class Listener:
    def __init__(self, server_ip: str, server_port: int):
        self.server_ip: str = server_ip
        self.server_port: int = server_port
        self.listening_socket: socket.socket
        self.running = True

    def start_listening(self):
        self.listening_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )  # ipv4 + tcp

        self.listening_socket.bind((self.server_ip, self.server_port))
        self.listening_socket.listen(20)

    def accept_connections(self):
        client_socket, client_ip = self.listening_socket.accept()
        connection = ClientConnection(client_socket)
        return connection

    def stop_listening(self):
        self.listening_socket.close()
