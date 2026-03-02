import unittest
from unittest.mock import MagicMock, patch
from socket_messenger.core.server.command_handler import CommandHandler, ParsedCommand
from socket_messenger.core.client.client_states import ClientStates


class TestCommandParsing(unittest.TestCase):

    def setUp(self):
        # Mock ServerManager
        self.smanager = MagicMock()
        self.chandler = CommandHandler(self.smanager)
        # Mock ClientManager
        self.client = MagicMock()
        self.client.get_username.return_value = "alice"
        self.client.get_state.return_value = ClientStates.MENU

    # ----------------- _parse_menu_command -----------------

    def test_command_without_argument_success(self):
        """Command that doesn't require argument returns ParsedCommand"""
        parsed = self.chandler._parse_menu_command(self.client, "ls")
        self.assertIsInstance(parsed, ParsedCommand)
        self.assertEqual(parsed.command, "ls")
        self.assertIsNone(parsed.argument)

    def test_command_with_argument_success(self):
        """Command that requires argument returns ParsedCommand with argument"""
        parsed = self.chandler._parse_menu_command(self.client, "connect bob")
        self.assertIsInstance(parsed, ParsedCommand)
        self.assertEqual(parsed.command, "connect")
        self.assertEqual(parsed.argument, "bob")

    def test_command_requires_argument_missing(self):
        """If command requires argument but none given, returns None and sends message"""
        parsed = self.chandler._parse_menu_command(self.client, "connect")
        self.assertIsNone(parsed)
        self.client.send_message.assert_called_with("This command requires an argument")

    def test_command_with_extra_argument(self):
        """If command has more than 1 argument, returns None and sends message"""
        parsed = self.chandler._parse_menu_command(self.client, "connect bob extra")
        self.assertIsNone(parsed)
        self.client.send_message.assert_called_with("Commands can't have more than 1 argument")

    def test_command_does_not_exist(self):
        """Unknown command returns None and sends error message"""
        parsed = self.chandler._parse_menu_command(self.client, "foobar")
        self.assertIsNone(parsed)
        self.client.send_message.assert_called_with("Command foobar doesn't exist")

    def test_command_no_arguments_given_for_non_argument_command(self):
        """Extra argument for command that doesn't take one returns None"""
        parsed = self.chandler._parse_menu_command(self.client, "ls extra")
        self.assertIsNone(parsed)
        self.client.send_message.assert_called_with("This command doesn't take any arguments")

    # ----------------- dispatch -----------------

    def test_dispatch_menu_state_calls_parse(self):
        """Dispatch in MENU state calls _handle_menu_state"""
        self.client.get_state.return_value = ClientStates.MENU
        with patch.object(self.chandler, "_handle_menu_state") as mock_menu, \
             patch.object(self.chandler, "_handle_chat_state") as mock_chat:

            self.chandler.dispatch(self.client, "ls")
            mock_menu.assert_called_once_with(self.client, "ls")
            mock_chat.assert_not_called()

    def test_dispatch_chat_state_calls_chat_handler(self):
        """Dispatch in CHAT state calls _handle_chat_state"""
        self.client.get_state.return_value = ClientStates.CHAT
        with patch.object(self.chandler, "_handle_chat_state") as mock_chat:
            self.chandler.dispatch(self.client, "hello")
            mock_chat.assert_called_once_with(self.client, "hello")

    def test_dispatch_empty_input(self):
        """Empty input returns None"""
        result = self.chandler.dispatch(self.client, "   ")
        self.assertIsNone(result)

    def test_dispatch_invalid_state(self):
        """Invalid state sends error message"""
        self.client.get_state.return_value = "weird_state"
        self.chandler.dispatch(self.client, "ls")
        self.client.send_message.assert_called_with("Invalid client state.")

    # ----------------- Handler methods -----------------

    def test_handle_connect_calls_smanager(self):
        self.chandler.handle_connect(self.client, "bob")
        self.smanager.handle_connect.assert_called_once_with(self.client, "bob")

    def test_handle_change_username_calls_smanager(self):
        self.chandler.handle_change_username(self.client, "charlie")
        self.smanager.handle_change_username.assert_called_once_with(self.client, "charlie")

    def test_handle_ls_sends_connected_clients(self):
        # simulate two clients: alice (self) and bob
        self.smanager.get_connected_clients_states.return_value = {
            "alice": ClientStates.MENU,
            "bob": ClientStates.CHAT
        }
        self.chandler.handle_ls(self.client)
        self.client.send_message.assert_called_once()
        sent_msg = self.client.send_message.call_args[0][0]
        self.assertIn("bob (unavailable)", sent_msg)
        self.assertNotIn("alice", sent_msg)

    def test_handle_display_menu_sends_menu(self):
        self.chandler.handle_display_menu(self.client)
        self.client.send_message.assert_called_once()
        sent_msg = self.client.send_message.call_args[0][0]
        self.assertIn("ls", sent_msg)
        self.assertIn("connect", sent_msg)

    def test_handle_disconnect_calls_smanager(self):
        self.chandler.handle_disconnect(self.client)
        self.smanager.handle_disconnect_client.assert_called_once_with(self.client)

if __name__ == "__main__":
    unittest.main()