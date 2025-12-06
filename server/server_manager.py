import socket
import threading
from typing import Callable

import client_manager
from session_manager import ses_manager
from client_states import ClientState


class smanager:
    def __init__(self, listening_addr='localhost', listening_port=5678,
                 all_options: dict[str, tuple[Callable, bool]] = {"ls":(client_manager.cmanager.display_all_client_names, False),
                                                                "disconnect":(client_manager.cmanager.disconnect_client, False),
                                                                "connect":(ses_manager.create_client_client_connections, True),
                                                                "username":(client_manager.cmanager.change_username, True)}):
        
        self.__listening_address = listening_addr
        self.__listening_port = listening_port
        self.__listening_socket: socket.socket = None
        self.__client_server_connections: dict[str, client_manager.cmanager] = {}

        self.__all_options = all_options
        self.__all_states: ClientState = ClientState

        self.__all_sessions: dict[str, ses_manager] = {}



    def create_listening_socket(self):
        self.__listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 + tcp
        server_address = (self.__listening_address, self.__listening_port)
        self.__listening_socket.bind(server_address)
        self.__listening_socket.listen(2)

        return 
    


    def create_client_server_connections(self):
        # accept client_server_connections
        while True:
            print("Waiting for new connections...")
            client_socket, client_addr = self.__listening_socket.accept()
            print(f"Incoming connection from {client_addr}")
            
            client_thread = threading.Thread(target=self.__handle_client_server_connection, args=(client_socket, client_addr))
            client_thread.daemon = True
            client_thread.start()
            

    def __handle_client_server_connection(self, client_socket: socket.socket, client_addr: str):
        print(f"The type of all_states is {type(self.__all_states)}")
        print(f"THREAD started for {client_addr}")
        username = self.__receive_and_check_username(client_socket)

        if not username:
            return
        
        new_cmanager = client_manager.cmanager(smanager=self,
                                            client_socket=client_socket,
                                            addr=client_addr,
                                            username=username,
                                            state=self.__all_states.MENU)
        
        self.__client_server_connections[username] = (new_cmanager)

        while new_cmanager.getState() != self.__all_states.DISCONNECTED:
            print("entered")
            new_cmanager.display_menu(self.__all_options)
            print(f"Waiting for chosen_option from {username}...")
            chosen_option = new_cmanager.receive()
            print(f"Raw chosen option from user {username} is {repr(chosen_option)}, the type is {type(chosen_option)}")
            self.dispatch_chosen_option(new_cmanager, chosen_option)


    def __receive_and_check_username(self, client_socket: socket.socket) -> str:
        client_socket.send("Please, enter you username otherwise you can't access this server".encode())
        print("Waiting for username input from...")
        username = client_socket.recv(512).decode().strip()
        print(f"Username received is {username} with type: {type(username)}")
        
        # drop connection if no username was entered
        if not username:
            client_socket.send("Sorry, you haven't entered a proper username.".encode())
            client_socket.close()
            return
        
        elif username in self.__client_server_connections:
            client_socket.send("Sorry, this username is not available, please enter another one.".encode())
            client_socket.close()
            return
        
        print(f"Username {username} is accepted")
        return username




    def dispatch_chosen_option(self, cmanager: client_manager.cmanager, chosen_option: str):
        chosen_option = chosen_option.strip()
        print(f"chosen option is chosen {chosen_option}")
        print(f"the type of the state on the client is {type(cmanager.getState())}")
        print(f"the type of the state in self.__all_states.CHAT: {type(self.__all_states.MENU)}")
        if cmanager.getState() == self.__all_states.CHAT: # define missing methods and properties\
            print("enetred chat")
            self.__all_sessions[cmanager.getName()].initialize_communication() # refer to already created session by another user

        elif cmanager.getState() == self.__all_states.MENU:
            print("entered menu")
        # check if chosen_option is available
            for option, (handler, is_special) in self.__all_options.items():
                if is_special and chosen_option.startswith(f"{option} "):
                    # check if only one arg was provided
                    parts = chosen_option.split()
                    if len(parts) != 2:
                        cmanager.send("Correct usage: <command> <argument>. Please try again, choose one of the following: ")
                        cmanager.display_menu(self.__all_options)
                        return self.dispatch_chosen_option()
                    
                    handler(cmanager, parts[1])
                    return
                
                elif not is_special and chosen_option==option:
                    print(f"handler for {chosen_option} is reached")
                    handler(cmanager)
                    return
            
            print ("skipped the loop")
            cmanager.send("Not a valid option, please try again: \n")
            return




###### HELPER METHODS ######

    def getConnections(self):
        return self.__client_server_connections
    
###### HELPER METHODS FOR CLIENT MANAGER ######

    def change_username(self, requester: client_manager.cmanager, old_username: str, new_username: str):
        # only allow client_manager to access this method 
        if not isinstance(requester, client_manager.cmanager):
            print("You are not a client manager, nothing is changed.")
            return
        
        self.__client_server_connections[new_username] = self.__client_server_connections[old_username]
        del self.__client_server_connections[old_username]

        return


    def disconnect_client(self, requester: client_manager.cmanager, username: str):
        if not isinstance(requester, client_manager.cmanager):
            print("You are not a client manager, nothing is changed.")
            return
        
        del self.__client_server_connections[username]
        return
    

###### HELPER METHODS FOR SESSION MANAGER ######
    
    def change_sessions(self, src_name: str, src_ses_manager: ses_manager, tgt_ses_manager: ses_manager):
        self.__all_sessions[src_name]=(src_ses_manager, tgt_ses_manager)
        return
    

    