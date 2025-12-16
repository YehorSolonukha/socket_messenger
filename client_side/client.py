import socket
import threading

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
        t1 = threading.Thread(target=self.__listen_for_input_and_send)
        t2 = threading.Thread(target=self.__listen_to_server_and_display)
        t1.start()
        t2.start()
        t2.join()


       

    
    def __listen_for_input_and_send(self):
        while True:
            message = input()
            if not message:
                continue
            try:
                self.__send(message)
            except:
                break


    def __listen_to_server_and_display(self):
        while True:
            try:
                response = self.__receive()
                if not response:
                    print("Server disconnected.")
                    break
                print(response)
            except ConnectionAbortedError:
                print("Server disconnected.")
                break
        return
        

    def __receive(self):
        response = self.socket.recv(1024).decode()
        return response
    
    def __send(self, message: str):
        self.socket.send(message.encode())
        return