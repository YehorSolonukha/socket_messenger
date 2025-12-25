from client_manager import ClientManager
from client_states import ClientStates


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

    def create_and_handle_client_to_client_communication(self):
        # check if target exist
        if not self.__check_if_target_exists():
            self.cmanagerSrc.send_message(
                "Target doesn't exist in our data base, please try again later"
            )
            return

        # check if target available
        if not self.__check_if_target_in_another_chat():
            self.cmanagerSrc.send_message(
                f"Unable to connect with {self.cmanagerTarget.get_username()}, user is in 'chat' mode... \n Please try again later"
            )
            return

        # set sessions for both
        self.__set_session_managers_for_both_clients()
        # change states for both to chat
        self.__set_states_for_both_clients(ClientStates.CHAT)

        # self.__set_sessions_in_global_dictionary()

        # notify target that it is chatting with source (probably not needed)
        # self.cmanagerTarget.send(f"You are now in chat with {self.cmanagerSrc.getName()}")

        # relay messages from source to target
        self.__notify_both_clients_about_established_connection()
        self.start_talking(requester=self)

        return

    # ---Direct communication between Clients (message relay)--- #

    def start_talking(self, requester, message: str = None):
        # check if requester is smanager or self
        # if not (isinstance(requester, 'smanager') or isinstance(requester, self)):
        #    print("Not autorized to use this method - 'initialize_communication()'")
        #    return

        if not message:
            message = self.cmanagerSrc.receive_message()

        while not self.__exit_condition_met():
            if message == "/exit":
                self.__set_exit_condition()
                self.__exit_condition_handler()
                return

            self.cmanagerTarget.send_message_include_sender(
                message, self.cmanagerSrc.get_username()
            )  # might be redundant
            message = self.cmanagerSrc.receive_message()

        self.__exit_condition_handler(message)
        return

    def __exit_condition_met(self):
        if not self.cmanagerSrc.get_session():
            return True
        return False

    def __exit_condition_handler(self, message: str = None):
        return message

    def __set_exit_condition(self):
        # change each client's session to None
        self.__set_session_managers_for_both_clients_to_none()

        # change each client's state back to MENU
        self.__set_states_for_both_clients(ClientStates.MENU)

        self.cmanagerSrc.send_message(
            f"The chat with {self.cmanagerTarget.get_username()} is over\n"
        )
        self.cmanagerSrc.show_menu()
        self.cmanagerTarget.send_message(
            f"The chat with {self.cmanagerSrc.get_username()} is over\n"
        )
        self.cmanagerTarget.show_menu()
        return

    # ---The end of direct communication--- #

    def __notify_both_clients_about_established_connection(self):
        self.cmanagerSrc.send_message(
            f"You entered a chat with {self.cmanagerTarget.get_username()}, please type /exit to exit.\n"
        )
        self.cmanagerTarget.send_message(
            f"You entered a chat with {self.cmanagerSrc.get_username()}, please type /exit to exit.\n"
        )
        return

    def __set_session_managers_for_both_clients(self):
        self.cmanagerSrc.change_session(self)

        target_session = SessionManager(
            self.cmanagerTarget, self.cmanagerSrc, self.smanager
        )
        self.cmanagerTarget.change_session(target_session)
        return

    def __set_session_managers_for_both_clients_to_none(self):
        self.cmanagerSrc.change_session(None)
        self.cmanagerTarget.change_session(None)
        return

    def __check_if_target_exists(self):
        if self.smanager.get_connections()[self.cmanagerTarget.get_username()]:
            return True
        return False

    def __check_if_target_in_another_chat(self):
        if self.cmanagerTarget.get_state() == ClientStates.MENU:
            return True
        elif self.cmanagerTarget.get_state() == ClientStates.CHAT:
            return False
        self.cmanagerSrc("Unknown error occured, please wait until we resolve it")
        print("New ClientState.STATE isn't handled")
        return

    def __set_states_for_both_clients(self, new_state: ClientStates):
        if not isinstance(new_state, ClientStates):
            print("The state is incorrect!")
            return
        self.cmanagerSrc.set_state(new_state)
        self.cmanagerTarget.set_state(new_state)
        return
