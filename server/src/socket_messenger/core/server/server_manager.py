"""
ServerManager is the central coordinator of the server.
It:
- Starts and listens for incoming client connections
- Spawns a dedicated thread per client
- Registers and tracks connected clients
- Manages username validation and changes
- Initiates client-to-client sessions via SessionManager
"""

# core functionality
import threading  # Used to handle multiple clients concurrently

# config
from dotenv import load_dotenv  # Loads environment variables from .env file
import os

# internal modules
from socket_messenger.core.client.client_states import ClientStates  # Enum/state definitions for clients

from socket_messenger.core.server.session_manager import (
    SessionManager,
)  # Manages client-to-client sessions
from socket_messenger.core.client.client_manager import (
    ClientManager,
)  # Handles logic for a single client

from socket_messenger.network.server_listener import Listener  # TCP server socket listener
from socket_messenger.network.client_connection import ClientConnection  # Wrapper over client socket I/O

from socket_messenger.storage.storage_manager import (
    StorageManager,
)  # Interacts with persistent storage

from socket_messenger.core.server.auth_manager import AuthManager # authenticates clients


# Load environment variables into the process
load_dotenv()


class ServerManager:
    """
    High-level server controller responsible for accepting connections,
    managing clients, and coordinating interactions between them.
    """

    def __init__(
        self,
        server_ip: str = os.getenv("LISTENING_ADDRESS").strip(),
        server_port: int = int(os.getenv("LISTENING_PORT").strip()),
    ):
        # Network configuration
        self._server_ip = server_ip
        self._server_port = server_port

        # Persistent storage configuration
        self._storage = StorageManager()

        # Authentication
        self._auth_manager = AuthManager(self._storage)

        # Active clients mapped by username
        self._client_server_connections: dict[str, ClientManager] = {}

        # Reference to all possible client states
        self._all_states: ClientStates = ClientStates

        # Active client-to-client sessions
        self._all_sessions: dict[str, tuple[SessionManager, SessionManager]] = {}


    #### INIT CONNECTION ####
    def run(self):
        """
        Starts the server listener and continuously accepts new clients.
        Each client is handled in a separate thread.
        """
        listener = Listener(self._server_ip, self._server_port)
        listener.start_listening()
        while listener.running:
            new_connection = listener.accept_connections()
            new_thread = threading.Thread(target=self.serve, args=(new_connection,))
            new_thread.start()

    #### SERVE #### 
    def serve(self, connection: ClientConnection):
        """
        Registers a new client and hands control over to its ClientManager.
        """
        print("new connection")
        username = self._auth_manager.authenticate_client(connection)
        if not username:
            connection.close_client_connection()
            return
        
        cl_manager = ClientManager(self, connection, username)

        # Store active client by username
        self._client_server_connections[cl_manager.get_username()] = cl_manager
        cl_manager.run()
    

    ###### HELPER METHODS ######
    def get_connections(self):
        """
        Returns all active client managers.
        """
        return self._client_server_connections

    def handle_connect(self, src_manager: ClientManager, target_username: str):
        """
        Initiates a client-to-client session if the target user exists
        and is not the same as the source user.
        """
        if not self._storage.client_exists(target_username):
            src_manager.send_message(f"User '{target_username}' doesn't exist")
            return

        if target_username == src_manager.get_username():
            src_manager.send_message("You cannot connect with yourself...")
            return
        
        if self._client_server_connections[target_username].is_in_chat():
            src_manager.send_message(
                f"Unable to connect with {target_username}, user is in 'chat' mode... \n Please try again later"
            )
            return

        target_manager = self._client_server_connections[target_username]

        # Create and start a session between two clients
        session = SessionManager(src_manager, target_manager, self)
        src_manager.set_session(session)
        target_manager.set_session(session)

    def handle_change_username(
        self,
        cl_manager: ClientManager,
        new_username: str
    ):
        """
        Changes a client's username if the new one is valid
        """
        old_username = cl_manager.get_username()
        if new_username == old_username:
            cl_manager.send_message(
                "What's the point of changing your username if it's the same as before?.."
            )
            return

        if new_username in self._client_server_connections:
            cl_manager.send_message("You cannot choose a name of an existing user")
            return

        # Update username in ClientManager
        cl_manager.set_username(new_username)

        # Update internal mapping
        self._client_server_connections[new_username] = self._client_server_connections[
            old_username
        ]
        del self._client_server_connections[old_username]

        cl_manager.send_message(
            f"Your username has been updated, your new username is {new_username}\n"
        )

        return new_username

    def handle_disconnect_client(self, cl_manager: ClientManager):
        """
        Disconnects a client and removes it from active connections.
        """
        cl_manager.disconnect_client()
        del self._client_server_connections[cl_manager.get_username()]
        return

    def get_connected_clients_states(self) -> dict[str, ClientStates]:
        """
        Returns a mapping of usernames to their current states.
        """
        info = {}
        for username, cl_manager in self._client_server_connections.items():
            info[username] = cl_manager.get_state()
        return info
