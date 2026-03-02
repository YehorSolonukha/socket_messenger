import unittest
from unittest.mock import MagicMock, patch

# Adjust these import paths if your actual project structure differs
from socket_messenger.core.server.session_manager import SessionManager
from socket_messenger.storage.message_manager import Message

class TestSessionManager(unittest.TestCase):

    def setUp(self):
        # Start patches for the managers so __init__ doesn't hit a real database
        self.patcher_storage = patch("socket_messenger.core.server.session_manager.StorageManager")
        self.patcher_message = patch("socket_messenger.core.server.session_manager.MessageManager")
        
        self.mock_storage_class = self.patcher_storage.start()
        self.mock_message_class = self.patcher_message.start()
        
        # Ensure patches are stopped after each test
        self.addCleanup(patch.stopall)

        # Setup Mock Clients
        self.cmanagerSrc = MagicMock()
        self.cmanagerSrc.get_username.return_value = "alice"

        self.cmanagerTarget = MagicMock()
        self.cmanagerTarget.get_username.return_value = "bob"

        self.smanager = MagicMock()

        # Initialize the target class
        self.session = SessionManager(
            self.cmanagerSrc,
            self.cmanagerTarget,
            self.smanager
        )

    # ---------------- __init__() ----------------
    def test_init_prepares_views_for_both_clients(self):
        self.assertTrue(self.session.active)
        self.cmanagerSrc.prepare_chat_view.assert_called_once_with("bob")
        self.cmanagerTarget.prepare_chat_view.assert_called_once_with("alice")

    # ---------------- relay() ----------------
    def test_relay_empty_message_is_ignored(self):
        self.session.relay(self.cmanagerSrc, "")
        self.session.relay(self.cmanagerSrc, None)
        
        self.cmanagerTarget.send_message_include_sender.assert_not_called()
        self.session.message_manager.save_message.assert_not_called()

    def test_relay_invalid_sender_is_ignored(self):
        unauthorized_sender = MagicMock()
        unauthorized_sender.get_username.return_value = "eve"
        
        self.session.relay(unauthorized_sender, "I am listening")
        
        self.cmanagerTarget.send_message_include_sender.assert_not_called()
        self.cmanagerSrc.send_message_include_sender.assert_not_called()
        self.session.message_manager.save_message.assert_not_called()

    def test_relay_standard_message_success(self):
        self.session.relay(self.cmanagerSrc, "Hello Bob!")
        
        # Verify Bob receives the message
        self.cmanagerTarget.send_message_include_sender.assert_called_once_with(
            "Hello Bob!", "alice"
        )
        
        # Verify the message manager was told to save the message
        self.session.message_manager.save_message.assert_called_once()
        
        # Optional: Verify the saved message object has the correct data
        args, _ = self.session.message_manager.save_message.call_args
        saved_msg = args[0]
        self.assertIsInstance(saved_msg, Message)
        self.assertEqual(saved_msg.sender, "alice")
        self.assertEqual(saved_msg.receiver, "bob")
        self.assertEqual(saved_msg.content, "Hello Bob!")

    # ---------------- _close() via relay() ----------------
    def test_relay_exit_command_closes_session(self):
        self.session.relay(self.cmanagerSrc, "/exit")
        
        self.assertFalse(self.session.active)
        
        # Verify internal _set_session_managers_for_both_clients_to_none logic
        self.cmanagerSrc.set_session.assert_called_once_with(None)
        self.cmanagerTarget.set_session.assert_called_once_with(None)
        
        # Verify closure notifications
        self.cmanagerSrc.send_message.assert_called_once_with("The chat with bob is over\n")
        self.cmanagerTarget.send_message.assert_called_once_with("The chat with alice is over\n")

if __name__ == "__main__":
    unittest.main()