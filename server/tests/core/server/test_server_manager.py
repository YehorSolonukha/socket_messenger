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
        src.get_username.return_value = "alice"
        self.smanager.handle_connect(src, "bob")
        src.send_message.assert_called_once_with("User 'bob' doesn't exist")

    def test_handle_connect_self(self):
        src = MagicMock()
        src.get_username.return_value = "alice"
        self.smanager._client_server_connections["alice"] = src
        self.smanager.handle_connect(src, "alice")
        src.send_message.assert_called_once_with("You cannot connect with yourself...")

    def test_handle_connect_success(self):
        src = MagicMock()
        src.get_username.return_value = "alice"
        tgt = MagicMock()
        tgt.get_username.return_value = "bob"
        self.smanager._client_server_connections = {
            "alice": src,
            "bob": tgt
        }
        with patch("socket_messenger.core.server.server_manager.SessionManager") as mock_sess:
            mock_sess_instance = mock_sess.return_value
            self.smanager.handle_connect(src, "bob")
            mock_sess.assert_called_once_with(src, tgt, self.smanager)
            mock_sess_instance.create_and_handle_client_to_client_communication.assert_called_once()

    # ---------------- get_connected_clients_states() ----------------
    def test_get_connected_clients_states(self):
        cm1 = MagicMock()
        cm1.get_state.return_value = ClientStates.MENU
        cm2 = MagicMock()
        cm2.get_state.return_value = ClientStates.CHAT
        self.smanager._client_server_connections = {
            "alice": cm1,
            "bob": cm2
        }
        states = self.smanager.get_connected_clients_states()
        self.assertEqual(states, {"alice": ClientStates.MENU, "bob": ClientStates.CHAT})

if __name__ == "__main__":
    unittest.main()