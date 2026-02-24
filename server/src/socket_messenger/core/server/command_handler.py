"""
This module handles parsing, validating, and dispatching user commands.
It:
- Routes user input based on client state (MENU vs CHAT)
- Validates commands and arguments
- Maps commands to handler functions
- Delegates server-level actions to ServerManager
"""

from typing import Callable, TYPE_CHECKING
from socket_messenger.core.client.client_states import ClientStates


class ParsedCommand:
    """
    Validated command.
    Holds the handler function, command name, and optional argument.
    """
    def __init__(self, handler: Callable, command: str, argument: str | None = None):
        self.command: str = command
        self.argument: str | None = argument
        self.handler: Callable = handler


class CommandHandler:
    """
    Central command router responsible for:
    - Dispatching input based on client state
    - Parsing and validating menu commands
    - Executing command handlers
    """
    def __init__(self, smanager: "ServerManager"):
        # Reference to ServerManager for server-wide operations
        self.smanager = smanager

        # Command registry:
        # command_name -> (handler, requires_argument, description)
        self._commands: dict[str, tuple[Callable, bool, str]] = {
            "ls": (self.handle_ls, False, " - list all users except you"),
            "disconnect": (self.handle_disconnect, False, " - disconnect from server"),
            "connect": (
                self.handle_connect,
                True,
                " <target_username> - enter chat with another user if available"
            ),
            "username": (
                self.handle_change_username,
                True,
                " <new_username> - change your username"
            ),
            "menu": (self.handle_display_menu, False, " - display all options again"),
        }

    ### VALIDATE & DISPATCH LOGIC ###
    def dispatch(self, cl_manager: "ClientManager", raw_input: str):
        """
        Entry point for processing client input.
        Dispatches handling logic based on the client's current state.
        """
        raw_input = raw_input.strip()

        if not raw_input:
            return

        match cl_manager.get_state():
            case ClientStates.CHAT:
                self._handle_chat_state(cl_manager, raw_input)
            case ClientStates.MENU:
                self._handle_menu_state(cl_manager, raw_input)
            case _:
                cl_manager.send_message("Invalid client state.")

    def _handle_menu_state(self, client_manager: "ClientManager", raw_input: str):
        """
        Parses and executes menu commands.
        """
        parsed_command = self._parse_menu_command(client_manager, raw_input)

        if parsed_command:
            if parsed_command.argument:
                parsed_command.handler(client_manager, parsed_command.argument)
                return

            parsed_command.handler(client_manager)
            return

    def _parse_menu_command(self, client_manager: "ClientManager", raw_input: str):
        """
        Validates menu command syntax and returns a ParsedCommand.
        """
        parts = raw_input.split()

        # Enforce at most one argument
        if len(parts) > 2:
            client_manager.send_message("Commands can't have more than 1 argument")
            return

        command = parts[0]

        # Check if command exists
        if command not in self._commands:
            client_manager.send_message(f"Command {command} doesn't exist")
            return
        


        handler = self._get_handler(command)

        # Command with argument
        if self._commands[command][1]:  # requires_argument
            if len(parts) == 1:
                client_manager.send_message("This command requires an argument")
                return
            if len(parts) == 2:
                argument = parts[1]
                if not argument:
                    client_manager.send_message("Argument can't be empty")
                    return

                parsed_command = ParsedCommand(handler, command, argument)
                return parsed_command

        # Command without argument
        elif not self._commands[command][1]:  # doesn't require argument
            if len(parts) == 1:
                parsed_command = ParsedCommand(handler, command)
                return parsed_command
            elif len(parts) == 2:
                client_manager.send_message("This command doesn't take any arguments")
                return
            

    def _handle_chat_state(self, client_manager: "ClientManager", raw_input: str):
        """
        Forwards chat messages to the active session.
        """
        client_manager.get_session().start_talking(
            self, raw_input
        )
        # Session was previously created by the user who initiated the chat

    ### HANDLERS (SPECIAL) ###
    def handle_connect(self, cl_manager: "ClientManager", target_username: str):
        """
        Requests ServerManager to initiate a client-to-client session.
        """
        self.smanager.handle_connect(cl_manager, target_username)

    def handle_change_username(self, cl_manager: "ClientManager", new_username: str):
        """
        Requests ServerManager to change the client's username.
        """
        self.smanager.handle_change_username(cl_manager, new_username)

    ### HANDLERS (NOT SPECIAL) ###
    def handle_ls(self, client_manager: "ClientManager"):
        """
        Lists all connected users except the requesting client,
        along with their availability status.
        """
        info = self.smanager.get_connected_clients_states()
        lines = []

        for username, state in info.items():
            if username == client_manager.get_username():
                continue

            match state:
                case ClientStates.CHAT:
                    status = "(unavailable)"
                case ClientStates.MENU:
                    status = ""
                case ClientStates.DISCONNECTED:
                    status = "(disconnected)"
                case _:
                    status = "(unknown status)"

            lines.append(f"\t- {username} {status}")

        if not lines:
            client_manager.send_message("There are no other users connected...")
            return

        message = "\n".join(lines)
        client_manager.send_message(message)
        return

    def handle_disconnect(self, cl_manager: "ClientManager"):
        """
        Disconnects the client from the server.
        """
        self.smanager.handle_disconnect_client(cl_manager)

    def handle_display_menu(self, cl_manager: "ClientManager"):
        """
        Displays all available commands and their descriptions.
        """
        menu = "\nHere are all available commmands: \n"

        for command, (*_, command_description) in self._commands.items():
            menu += f"\t- {command + command_description}\n"

        cl_manager.send_message(menu)
        return

    def _get_handler(self, command: str) -> Callable:
        """
        Retrieves the handler function for a given command.
        """
        return self._commands[command][0]
