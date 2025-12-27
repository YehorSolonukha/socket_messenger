import socket
import threading
from typing import Callable

import client_manager
from session_manager import SessionManager
from client_states import ClientStates


class ServerManager:
    def __init__(
        self,
        listening_addr="localhost",
        listening_port=5678,
        all_options: dict[str, tuple[Callable, bool]] = {
            "ls": (client_manager.ClientManager.show_available_clients, False),
            "disconnect": (client_manager.ClientManager.disconnect_client, False),
            "connect": (
                SessionManager.create_and_handle_client_to_client_communication,
                True,
            ),
            "username": (client_manager.ClientManager.set_username, True),
            "menu": (client_manager.ClientManager.show_menu, False),
        },
    ):

        self.__listening_address = listening_addr
        self.__listening_port = listening_port
        self.__listening_socket: socket.socket = None
        self.__client_server_connections: dict[str, client_manager.ClientManager] = {}

        self.__all_options = all_options
        self.__all_states: ClientStates = ClientStates

        self.__all_sessions: dict[str, tuple[SessionManager, SessionManager]] = {}

    def listen_for_new_connections(self):
        self.__listening_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )  # ipv4 + tcp
        server_address = (self.__listening_address, self.__listening_port)
        self.__listening_socket.bind(server_address)
        self.__listening_socket.listen(20)

        return

    def accept_and_handle_incoming_connections(self):
        # accept client_server_connections
        while True:
            print("Waiting for new connections...")
            client_socket, client_addr = self.__listening_socket.accept()
            print(f"Incoming connection from {client_addr}")

            client_thread = threading.Thread(
                target=self.__handle_connection,
                args=(client_socket, client_addr),
            )
            client_thread.daemon = True
            client_thread.start()

    def __handle_connection(self, client_socket: socket.socket, client_addr: str):
        print(f"The type of all_states is {type(self.__all_states)}")
        print(f"THREAD started for {client_addr}")
        username = self.__ask_for_and_verify_username(client_socket)

        if not username:
            return

        new_cmanager = client_manager.ClientManager(
            smanager=self,
            client_socket=client_socket,
            addr=client_addr,
            username=username,
            state=self.__all_states.MENU,
        )

        self.__client_server_connections[username] = new_cmanager

        new_cmanager.show_menu(self.__all_options)
        while new_cmanager.get_state() != self.__all_states.DISCONNECTED:
            print(f"Waiting for chosen_option from {username}...")
            chosen_option = new_cmanager.receive_message()
            print(
                f"Raw chosen option from user {username} is {repr(chosen_option)}, the type is {type(chosen_option)}"
            )
            self.__dispatch_chosen_option(new_cmanager, chosen_option)

    def __ask_for_and_verify_username(self, client_socket: socket.socket) -> str:
        client_socket.send(
            "Please, enter you username otherwise you can't access this server".encode()
        )
        print("Waiting for username input from...")
        username = client_socket.recv(512).decode().strip()
        print(f"Username received is {username} with type: {type(username)}")

        # drop connection if no username was entered
        if not username:
            client_socket.send("Sorry, you haven't entered a proper username.".encode())
            client_socket.close()
            return

        elif username in self.__client_server_connections:
            client_socket.send(
                "Sorry, this username is not available, please enter another one.".encode()
            )
            client_socket.close()
            return

        print(f"Username {username} is accepted")
        return username

    def __dispatch_chosen_option(
        self, cmanager: client_manager.ClientManager, chosen_option: str
    ):
        chosen_option = chosen_option.strip()
        print(f"chosen option is chosen {chosen_option}")
        if (
            cmanager.get_state() == self.__all_states.CHAT
        ):  # define missing methods and properties\
            print("entered chat")
            self.__client_server_connections[
                cmanager.get_username()
            ].get_session().start_talking(
                self, chosen_option
            )  # refer to already created session by another user

        elif cmanager.get_state() == self.__all_states.MENU:
            print("entered menu")
            # check if chosen_option is available
            for option, (handler, is_special) in self.__all_options.items():
                if is_special and chosen_option.startswith(f"{option} "):
                    # check if only one arg was provided
                    parts = chosen_option.split()
                    if len(parts) != 2:
                        cmanager.send_message(
                            "Correct usage: <command> <argument>. Please try again, choose one of the following: "
                        )
                        cmanager.show_menu(self.__all_options)
                        return

                    # handler for connect
                    if chosen_option.startswith("connect "):
                        # check if user exists
                        if parts[1] not in self.__client_server_connections.keys():
                            cmanager.send_message(f"User '{parts[1]}' doesn't exist")
                            cmanager.show_menu()
                            return

                        new_ses_manager = SessionManager(
                            cmanagerSrc=cmanager,
                            cmanagerTarget=self.__client_server_connections[parts[1]],
                            smanager=self,
                        )
                        handler(new_ses_manager)
                        return

                    print(f"BUG - parts: {parts}")
                    handler(cmanager, parts[1])
                    return

                elif not is_special and chosen_option == option:
                    print(f"handler for {chosen_option} is reached")
                    handler(cmanager)
                    return

            print("skipped the loop")
            cmanager.send_message("Not a valid option, please try again: \n")
            return

    ###### HELPER METHODS ######

    def get_connections(self):
        return self.__client_server_connections

    ###### HELPER METHODS FOR CLIENT MANAGER ######

    def set_username(
        self,
        requester: client_manager.ClientManager,
        old_username: str,
        new_username: str,
    ):
        # only allow client_manager to access this method
        if not isinstance(requester, client_manager.ClientManager):
            print("You are not a client manager, nothing is changed.")
            return

        self.__client_server_connections[new_username] = (
            self.__client_server_connections[old_username]
        )
        del self.__client_server_connections[old_username]

        requester.send_message(
            f"Your username has been updated, your new username is {new_username}\n"
        )

        return

    def disconnect_client(self, requester: client_manager.ClientManager, username: str):
        if not isinstance(requester, client_manager.ClientManager):
            print("You are not a client manager, nothing is changed.")
            return

        del self.__client_server_connections[username]
        return

    def get_options_from_menu(self):
        return self.__all_options


###### HELPER METHODS FOR SESSION MANAGER ######

# def update_sessions(self, src_name: str, src_ses_manager: ses_manager, tgt_ses_manager: ses_manager):
#    self.__all_sessions[src_name]=(src_ses_manager, tgt_ses_manager)
#    return
