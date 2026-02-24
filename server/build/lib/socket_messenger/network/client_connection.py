import socket

class ClientConnection:
    def __init__(self, socket: socket.socket):
        self.socket: socket.socket = socket
        self.running = True

    def send_to_client(self, message: str) -> None:
        if not self.running:
            self.close_client_connection()
            return
        self.socket.send(message.encode())

    def receive_from_client(self) -> str:
        if not self.running:
            return
        message = self.socket.recv(1024).decode()
        if not message:
            self.close_client_connection()
            return
        return message.strip()

    def close_client_connection(self):
        if self.running == False:
            return
        self.socket.close()
        self.running = False
