from socket_messenger.core.client.client_states import ClientStates
from socket_messenger.network.client_connection import ClientConnection
from socket_messenger.core.server.command_handler import CommandHandler

class ClientManager:
    def __init__(
        self,
        smanager: "server_manager.ServerManager",
        connection: ClientConnection,
        username: str
    ):
        self._username = username
        self.connection: ClientConnection = connection
        self._state: ClientStates

        self._smanager = smanager

        self.command_handler = CommandHandler(self._smanager)
        self.session = None


    # main loop
    def run(self):
        self._state = ClientStates.MENU
        self.command_handler.handle_display_menu(self)
        while True:
            try:
                message = self.receive_message()
                if not message:
                    self.disconnect_client()
                    break
            except Exception as e:
                print(repr(e))
                self.disconnect_client()
                break
            if self.is_in_chat():
                self.session.relay(self, message)
            self.command_handler.dispatch(self, message)

    # basic IO
    def send_message(self, message: str):
        self.connection.send_to_client(message)
        return

    def send_message_include_sender(self, message: str, sender: str):
        message = f"{sender}: {message}"
        self.connection.send_to_client(message)
        return

    def receive_message(self):
        message = self.connection.receive_from_client()
        return message

    # session management
    def disconnect_client(self):
        self.connection.close_client_connection()
        self.set_state(ClientStates.DISCONNECTED)
        return

    # getters/setters
    def set_session(self, new_session):
        self.set_session = new_session
        if new_session:
            self.set_state(ClientStates.CHAT)
            return
        self.set_state(ClientStates.MENU)

    def set_username(self, new_username: str):
        self._username = new_username

    def set_state(self, new_state: ClientStates):
        if not isinstance(new_state, ClientStates):
            print(
                "[ERROR] - the state isn't changed, not a member of enum - ClientState"
            )
            return
        self._state = new_state
        return

    def set_session(self, session):
        self.session = session
        return

    def get_username(self):
        return self._username

    def get_state(self):
        return self._state

    def get_session(self):
        return self.session
    
    # helpers
    def is_in_chat(self) -> bool:
        if self.get_state() == ClientStates.CHAT:
            return True
        return False
