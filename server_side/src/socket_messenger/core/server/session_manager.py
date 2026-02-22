from socket_messenger.core.client.client_manager import ClientManager
from socket_messenger.core.client.client_states import ClientStates
from socket_messenger.storage.storage_manager import StorageManager


class SessionManager:
    def __init__(
        self,
        cmanagerSrc: ClientManager,
        cmanagerTarget: ClientManager,
        smanager: "ServerManager",
    ):
        self.cmanagerSrc = cmanagerSrc
        self.cmanagerTarget = cmanagerTarget
        self.smanager = smanager
        self.storage_manager = StorageManager()

    def create_and_handle_client_to_client_communication(self):
        self._notify_both_clients_about_established_connection()
        return

    
    # ---Direct communication between Clients (message relay)--- #

    def relay(self, sender: ClientManager, message: str = None):
        if not message:
            return

        if message == "/exit":
            self._set_exit_condition()
            self._exit_condition_handler(message)
            return

        if sender is self.cmanagerSrc:
            self.cmanagerTarget.send_message_include_sender(
                message, sender.get_username()
            )
            return
        self.cmanagerSrc.send_message_include_sender(
                message, sender.get_username()
            )

    def _exit_condition_met(self):
        if not self.cmanagerSrc.get_session() and self.cmanagerSrc.get_state() == ClientStates.MENU:
            return True
        return False

    def _exit_condition_handler(self, message: str = None):
        self.cmanagerSrc.send_message(
            f"The chat with {self.cmanagerTarget.get_username()} is over\n"
        )
        
        self.cmanagerTarget.send_message(
            f"The chat with {self.cmanagerSrc.get_username()} is over\n"
        )
        
        return message

    def _set_exit_condition(self):
        self._set_session_managers_for_both_clients_to_none()

        self._set_states_for_both_clients(ClientStates.MENU)
        return

    # ---The end of direct communication--- #

    def _notify_both_clients_about_established_connection(self):
        self.cmanagerSrc.send_message(
            f"You entered a chat with {self.cmanagerTarget.get_username()}, please type /exit to exit.\n"
        )
        self.cmanagerTarget.send_message(
            f"You entered a chat with {self.cmanagerSrc.get_username()}, please type /exit to exit.\n"
        )
        return

    def _set_session_managers_for_both_clients_to_none(self):
        self.cmanagerSrc.set_session(None)
        self.cmanagerTarget.set_session(None)
        return

# TO BE CHANGED ->
    def _check_if_target_exists(self):
        if self.smanager.get_connections()[self.cmanagerTarget.get_username()]:
            return True
        return False

    def _check_if_target_in_another_chat(self):
        if self.cmanagerTarget.get_state() == ClientStates.MENU:
            return True
        elif self.cmanagerTarget.get_state() == ClientStates.CHAT:
            return False
        self.cmanagerSrc.send_message("Unknown error occured, please wait until we resolve it")
        print("New ClientState.STATE isn't handled")
        return
# <- TO BE CHANGED

    def _set_states_for_both_clients(self, new_state: ClientStates):
        if not isinstance(new_state, ClientStates):
            print("The state is incorrect!")
            return
        self.cmanagerSrc.set_state(new_state)
        self.cmanagerTarget.set_state(new_state)
        return
