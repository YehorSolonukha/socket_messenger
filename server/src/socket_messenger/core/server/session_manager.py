from datetime import datetime

from socket_messenger.core.client.client_manager import ClientManager
from socket_messenger.core.client.client_states import ClientStates

from socket_messenger.storage.storage_manager import StorageManager
from socket_messenger.storage.message_manager import MessageManager, Message

class SessionManager:
    def __init__(
        self,
        cmanagerSrc: ClientManager,
        cmanagerTarget: ClientManager,
        smanager: "ServerManager",
    ):
        self.active = True

        self.cmanagerSrc = cmanagerSrc
        self.cmanagerTarget = cmanagerTarget
        self.smanager = smanager

        self.storage_manager = StorageManager()
        self.message_manager = MessageManager(self.storage_manager)
        
        self.cmanagerSrc.prepare_chat_view(self.cmanagerTarget.get_username())
        self.cmanagerTarget.prepare_chat_view(self.cmanagerSrc.get_username())


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
            receiver = self.cmanagerTarget
        else:
            receiver = self.cmanagerSrc

        receiver.send_message_include_sender(
            message, sender.get_username()
        )
        message_to_save = Message(sender.get_username(), receiver.get_username(), message, datetime.now())
        self.message_manager.save_message(message_to_save)


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

    def _set_session_managers_for_both_clients_to_none(self):
        self.cmanagerSrc.set_session(None)
        self.cmanagerTarget.set_session(None)
        return
