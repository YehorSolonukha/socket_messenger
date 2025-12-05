import socket
from client_states import ClientState
from session_manager import ses_manager


class cmanager:
    def __init__(self, smanager: "server_manager.smanager", client_socket: socket.socket, addr: str, 
                 username: str, state: ClientState, chat_partner: cmanager):
        self.__username = username
        self.__client_socket = client_socket
        self.__addr = addr
        self.__state: ClientState = state
        
        self.__smanager = smanager
        self.__ses_manager: ses_manager = None


    def send(self, message: str):
        self.__client_socket.send(message.encode())
        return
    
    def send_named(self, message: str, sender: str):
        message = f"{sender}: {message}"
        self.__client_socket.send(message.encode())
        return
    

    def receive(self):
        message = self.__client_socket.recv(1024).decode()
        return message


    def display_menu(self, options: dict):
        # create a menu
        message = "Please choose one of the following options: \n"
        for key in options.keys():
            message += f"{key}: {options[key]}\n"
        
        # send the menu
        self.__client_socket.send(message.encode())
        return
    

    def display_all_client_names(self):
        connections = self.__smanager.getConnections().keys()
        client_names=""
        for name in connections:
            client_names+=name + "\n"
        self.send(client_names)
        return 

    
    def disconnect_client(self):
        self.__client_socket.close()
        return self.__smanager.disconnect_client(self.__username)

    
    def change_username(self, new_username: str):
        # update name in instance of this class
        old_username = self.__username
        self.__username = new_username
        # update name server wide
        return self.__smanager.change_username(self, old_username=old_username, new_username=new_username)


    def change_state(self, new_state: str):
            #TODO
            return
    
    def change_session(self, session: ses_manager):
        self.__ses_manager = ses_manager
        return


    def getName(self):
        return self.__username
    

    def getState(self):
        return self.__state
    
    def getSession(self):
        return self.__ses_manager
    
    