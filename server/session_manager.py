from client_manager import cmanager
from client_states import ClientState


class ses_manager():
    def __init__(self, cmanagerSrc: cmanager, cmanagerTarget: cmanager, smanager: "smanager"):
        self.cmanagerSrc = cmanagerSrc
        self.cmanagerTarget = cmanagerTarget
        self.smanager = smanager


    def create_client_client_connections(self):
        # check if target exist
        if not self.__check_if_target_exists():
            self.cmanagerSrc.send("Target doesn't exist in our data base, please try again later")
            return
        
        # check if target available
        if not self.__check_if_target_available():
            self.cmanagerSrc.send(f"Unable to connect with {self.cmanagerTarget.getName()}, user is in 'chat' mode... \n Please try again later")
            return
        

        # set sessions for both
        self.__set_sessions_in_cmanagers()
        # change states for both
        self.__change_states_to_chat()
        
        #self.__set_sessions_in_global_dictionary()

        # notify target that it is chatting with source (probably not needed)
        # self.cmanagerTarget.send(f"You are now in chat with {self.cmanagerSrc.getName()}")

        # relay messages from source to target
        self.__announce_established_connection_to_both_clients()
        self.initialize_communication(requester=self)

        return
    

# ---Direct communication between Clients (message relay)--- #

    def initialize_communication(self, requester, message: str = None):
        # check if requester is smanager or self
        #if not (isinstance(requester, 'smanager') or isinstance(requester, self)):
        #    print("Not autorized to use this method - 'initialize_communication()'")
        #    return

        if not message:
            message = self.cmanagerSrc.receive()

        while not self.__exit_condition_met():
            if message=='/exit':
                self.__set_exit_condition()
                break
            
            self.cmanagerTarget.send_named(message, self.cmanagerSrc.getName())

            if not self.__exit_condition_met(): # might be redundant
                message = self.cmanagerSrc.receive()
            else:
                break
        
        self.__exit_condition_handler()
        return

    
    def __exit_condition_met(self):
        pass

    def __exit_condition_handler(self):
        pass
    
    def __set_exit_condition(self):
        # change each client's session to None
        self.__set_sessions_in_cmanagers_to_None()

        # change each client's state back to MENU
        self.__change_states_to_menu()
        return
    
# ---The end of direct communication--- #

    def __announce_established_connection_to_both_clients(self):
        self.cmanagerSrc.send(f"You entered a chat with {self.cmanagerTarget.getName()}, please type /exit to exit.\n")
        self.cmanagerTarget.send(f"You entered a chat with {self.cmanagerSrc.getName()}, please type /exit to exit.\n")
        return
    
    
    def __set_sessions_in_cmanagers(self):
        self.cmanagerSrc.change_session(self)

        target_session = ses_manager(self.cmanagerTarget, self.cmanagerSrc, self.smanager)
        self.cmanagerTarget.change_session(target_session)
        return 


    def __check_if_target_exists(self):
        if self.smanager.getConnections()[self.cmanagerTarget.getName()]:
            return True
        return False
    


    def __check_if_target_available(self):
        if self.cmanagerTarget.getState() == ClientState.MENU:
            return True
        elif self.cmanagerTarget.getState() == ClientState.CHAT:
            return False
        self.cmanagerSrc("Unknown error occured, please wait until we resolve it")
        print("New ClientState.STATE isn't handled")
        return


    

    def __change_states_to_chat(self):
        self.cmanagerSrc.change_state(ClientState.CHAT)
        self.cmanagerTarget.change_state(ClientState.CHAT)
        return
    

