import unittest
from unittest.mock import MagicMock, patch
from socket_messenger.core.client.client_manager import ClientManager
from socket_messenger.core.client.client_states import ClientStates

class TestClientManager(unittest.TestCase):

    def setUp(self):
        # Patching dependencies that are instantiated inside __init__
        self.patcher_cmd = patch("socket_messenger.core.client.client_manager.CommandHandler")
        self.patcher_msg = patch("socket_messenger.core.client.client_manager.MessageManager")
        
        self.mock_cmd_class = self.patcher_cmd.start()
        self.mock_msg_class = self.patcher_msg.start()
        
        self.addCleanup(patch.stopall)

        self.mock_smanager = MagicMock()
        self.mock_connection = MagicMock()
        self.username = "alice"

        self.cmanager = ClientManager(
            self.mock_smanager, 
            self.mock_connection, 
            self.username
        )

    # ---------------- State & Username ----------------

    def test_set_state_valid(self):
        self.cmanager.set_state(ClientStates.CHAT)
        self.assertEqual(self.cmanager.get_state(), ClientStates.CHAT)

    def test_set_state_invalid(self):
        # Should not change state if not a ClientStates enum member
        self.cmanager._state = ClientStates.MENU
        self.cmanager.set_state("NOT_A_STATE")
        self.assertEqual(self.cmanager.get_state(), ClientStates.MENU)

    # ---------------- IO Operations ----------------

    def test_send_message(self):
        self.cmanager.send_message("test message")
        self.mock_connection.send_to_client.assert_called_once_with("test message")

    def test_receive_message(self):
        self.mock_connection.receive_from_client.return_value = "hello"
        msg = self.cmanager.receive_message()
        self.assertEqual(msg, "hello")

    # ---------------- Run Loop Logic ----------------

    def test_run_loop_dispatches_command_in_menu(self):
        # Mock receive_message to return a command, then None to break loop
        self.cmanager.receive_message = MagicMock(side_effect=["/help", None])
        self.cmanager._state = ClientStates.MENU
        
        # We also need to mock disconnect_client so the test doesn't actually close things
        self.cmanager.disconnect_client = MagicMock()

        self.cmanager.run()

        # Check if dispatch was called with the message
        self.cmanager.command_handler.dispatch.assert_called_with(self.cmanager, "/help")
        self.cmanager.disconnect_client.assert_called_once()

    # ---------------- Session & View ----------------

    def test_set_session_none_returns_to_menu(self):
        self.cmanager.set_session(None)
        self.assertEqual(self.cmanager.get_state(), ClientStates.MENU)
        self.assertIsNone(self.cmanager.session)

    @patch.object(ClientManager, 'display_previous_messages')
    def test_prepare_chat_view(self, mock_display_prev):
        self.cmanager.prepare_chat_view("bob")
        
        # Should clear screen (send newlines) and send entry message
        self.mock_connection.send_to_client.assert_any_call("You entered a chat with bob. To return to main menu - issue /exit command")
        mock_display_prev.assert_called_once()

    def test_display_previous_messages(self):
        # Setup mock messages
        msg1 = MagicMock(sender="bob", content="hi", timestamp="12:00")
        msg2 = MagicMock(sender="alice", content="hey", timestamp="12:01")
        self.cmanager.message_manager.get_messages_between.return_value = [msg1, msg2]
        
        self.cmanager.display_previous_messages("bob")
        
        # Verify formatting for both sender and receiver
        self.mock_connection.send_to_client.assert_any_call("12:00 | bob: hi")
        self.mock_connection.send_to_client.assert_any_call("12:01 |  hey")

if __name__ == "__main__":
    unittest.main()