import socket

class Client:
    def __init__(self, server_address: str = 'localhost', server_port: int = 5678):
        self.socket = None
        self.server_address = server_address
        self.server_port = server_port


    def establish_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_address, self.server_port))
        return
    

    def receive_the_menu(self):
        menu = self.__receive()
        print(menu)
        return
    


    def talk_to_server(self):
        while True:
            message = input()
            self.__send(message)
            
            try:
                response = self.__receive()
            except ConnectionAbortedError:
                print("Server disconnected.")
                break
            
            print(response)
    

    def __receive(self):
        response = self.socket.recv(1024).decode()
        return response
    
    def __send(self, message: str):
        self.socket.send(message.encode())
        return