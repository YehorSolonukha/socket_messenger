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
        self.active = True

        self._notify_both_clients_about_established_connection()


    def relay(self, sender: ClientManager, message: str = None):
        if not message:
            return
        
        if sender is not self.cmanagerSrc and sender is not self.cmanagerTarget:
            print("Sender not part of this session")
            return

        if message == "/exit":
            self._close()
            return

        if sender is self.cmanagerSrc:
            self.cmanagerTarget.send_message_include_sender(
                message, sender.get_username()
            )
            return
        
        self.cmanagerSrc.send_message_include_sender(
                message, sender.get_username()
            )


    def _close(self):
        if not self.active:
            return
        self.active = False

        self._set_session_managers_for_both_clients_to_none()

        self.cmanagerSrc.send_message(
            f"The chat with {self.cmanagerTarget.get_username()} is over\n"
        )
        
        self.cmanagerTarget.send_message(
            f"The chat with {self.cmanagerSrc.get_username()} is over\n"
        )


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
