import socket
from dotenv import load_dotenv


class Network():
    def __init__(
        self,
        server_address: str,
        server_port: int,
    ):
        self._socket: socket.socket|None = None
        # socket config
        self.server_address: str = server_address
        self.server_port: int = server_port

    def connect_to_server(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.server_address, self.server_port))
        return

    def send_to_server(self, message: str):
        self._socket.send(message.encode())

    def receive_from_server(self):
        if not self._socket:
            return ""

        try:
            return self._socket.recv(1024).decode()
        except OSError:
            return ""


    def close_server_connection(self):
        if not self._socket:
            return 
        
        self._socket.close()
        return
