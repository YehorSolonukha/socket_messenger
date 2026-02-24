import sys

sys.path.insert(
    0,
    "C:\\Users\\YehorSolonukha\\My_Career\DevOps\\05_Python\\communicator\\client-server\\main\\client_side\\src",
)

import unittest
from unittest.mock import Mock
from core import Core


class TestCore(unittest.TestCase):

    def setUp(self):
        self.mock_network = Mock()
        self.mock_ui = Mock()
        self.core = Core(self.mock_network, self.mock_ui)

    # on_user_input
    def test_on_user_input_send_message_when_running(self):
        self.core.running = True
        message = "Hello"
        self.core.on_user_input(message)
        self.mock_network.send_to_server.assert_called_once_with(message)

    def test_on_user_input_doesnt_send_message_when_not_running(self):
        self.core.running = False
        message = "Hello"
        self.core.on_user_input(message)
        self.mock_network.send_to_server.assert_not_called()

    def test_on_user_input_doesnt_send_message_when_message_is_empty_string(self):
        self.core.on_user_input('')
        self.mock_network.send_to_server.assert_not_called()

    # on_server_message
    def test_on_server_message_stop_when_None_message(self):
        self.core.on_server_message(None)

        self.mock_ui.display.assert_called_once_with("Server disconnected.")
        self.assertFalse(self.core.running)
        self.mock_network.close_server_connection.assert_called_once()

    def test_on_server_message_stop_when_empty_string(self):
        self.core.on_server_message("")

        self.mock_ui.display.assert_called_once_with("Server disconnected.")
        self.assertFalse(self.core.running)
        self.mock_network.close_server_connection.assert_called_once()

    def test_on_server_message_display_when_message(self):
        self.core.on_server_message("Hello")
        self.mock_ui.display.assert_called_once_with("Hello")

    # stop
    def test_stop_can_be_called_twice_safely(self):
        self.core.stop()
        self.core.stop()

        self.assertFalse(self.core.running)
        self.mock_network.close_server_connection.assert_called_once()


if __name__ == "__main__":
    unittest.main()
