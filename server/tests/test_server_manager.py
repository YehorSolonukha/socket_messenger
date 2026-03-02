import os
os.environ["LISTENING_PORT"] = "5678"
os.environ["LISTENING_ADDRESS"] = "0.0.0.0"

import unittest
from unittest.mock import MagicMock, patch
from socket_messenger.core.server.server_manager import ServerManager
from socket_messenger.core.client.client_states import ClientStates


class TestServerManager(unittest.TestCase):

    def setUp(self):
        self.smanager = ServerManager()
        # patch storage & auth manager to avoid real DB calls
        self.smanager._storage = MagicMock()
        self.smanager._auth_manager = MagicMock()

    # ---------------- handle_change_username() ----------------
    def test_change_username_same_name(self):
        client = MagicMock()
        client.get_username.return_value = "alice"
        result = self.smanager.handle_change_username(client, "alice")
        self.assertIsNone(result)
        client.send_message.assert_called_once()

    def test_change_username_taken(self):
        # simulate existing user
        client = MagicMock()
        client.get_username.return_value = "alice"
        self.smanager._client_server_connections["bob"] = MagicMock()
        result = self.smanager.handle_change_username(client, "bob")
        self.assertIsNone(result)
        client.send_message.assert_called_once()

    def test_change_username_success(self):
        client = MagicMock()
        client.get_username.return_value = "alice"
        self.smanager._client_server_connections["alice"] = client
        result = self.smanager.handle_change_username(client, "charlie")
        self.assertEqual(result, "charlie")
        self.assertIn("charlie", self.smanager._client_server_connections)
        self.assertNotIn("alice", self.smanager._client_server_connections)
        client.send_message.assert_called_once()

    # ---------------- handle_disconnect_client() ----------------
    def test_disconnect_client_removes_from_connections(self):
        client = MagicMock()
        client.get_username.return_value = "alice"
        self.smanager._client_server_connections["alice"] = client
        self.smanager.handle_disconnect_client(client)
        self.assertNotIn("alice", self.smanager._client_server_connections)
        client.disconnect_client.assert_called_once()

    # ---------------- handle_connect() ----------------
    def test_handle_connect_user_does_not_exist(self):
        src = MagicMock()
        target_name = "ghost_user"
        # Mock storage to say user doesn't exist
        self.smanager._storage.client_exists.return_value = False

        self.smanager.handle_connect(src, target_name)

        src.send_message.assert_called_once_with(f"User '{target_name}' doesn't exist")

    def test_handle_connect_with_self(self):
        src = MagicMock()
        src.get_username.return_value = "alice"
        self.smanager._storage.client_exists.return_value = True

        self.smanager.handle_connect(src, "alice")

        src.send_message.assert_called_once_with("You cannot connect with yourself...")

    def test_handle_connect_target_already_in_chat(self):
        src = MagicMock()
        src.get_username.return_value = "alice"
        
        target = MagicMock()
        target.is_in_chat.return_value = True
        
        self.smanager._storage.client_exists.return_value = True
        self.smanager._client_server_connections["bob"] = target

        self.smanager.handle_connect(src, "bob")

        src.send_message.assert_called_with(
            "Unable to connect with bob, user is in 'chat' mode... \n Please try again later"
        )

    @patch("socket_messenger.core.server.server_manager.SessionManager")
    def test_handle_connect_success(self, MockSession):
        """
        Tests the happy path where a session is successfully created 
        and assigned to both managers.
        """
        # Setup source
        src = MagicMock()
        src.get_username.return_value = "alice"
        
        # Setup target
        target = MagicMock()
        target.is_in_chat.return_value = False
        
        self.smanager._storage.client_exists.return_value = True
        self.smanager._client_server_connections["bob"] = target

        # Execute
        self.smanager.handle_connect(src, "bob")

        # Verify SessionManager was instantiated with correct args
        MockSession.assert_called_once_with(src, target, self.smanager)
        
        # Verify both managers received the new session object
        session_instance = MockSession.return_value
        src.set_session.assert_called_once_with(session_instance)
        target.set_session.assert_called_once_with(session_instance)

    # ---------------- get_connected_clients_states() ----------------
    def test_get_connected_clients_states(self):
        cm1 = MagicMock()
        cm1.get_state.return_value = ClientStates.MENU
        cm2 = MagicMock()
        cm2.get_state.return_value = ClientStates.CHAT
        self.smanager._client_server_connections = {"alice": cm1, "bob": cm2}
        states = self.smanager.get_connected_clients_states()
        self.assertEqual(states, {"alice": ClientStates.MENU, "bob": ClientStates.CHAT})


if __name__ == "__main__":
    unittest.main()
