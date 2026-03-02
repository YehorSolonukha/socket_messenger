import unittest
from unittest.mock import patch, MagicMock

from socket_messenger.core.server.auth_manager import AuthManager

class TestPasswordValidation(unittest.TestCase):

    def setUp(self):
        self.auth = AuthManager(
            storage=MagicMock()
        )

    def test_valid_password(self):
        success, msg = self.auth._validate_password_format("ab12c")
        self.assertTrue(success)
        self.assertEqual(msg, "")

    def test_too_short_password(self):
        success, msg = self.auth._validate_password_format("a1b")
        self.assertFalse(success)
        self.assertIn("too short", msg)

    def test_not_enough_digits(self):
        success, msg = self.auth._validate_password_format("abcde")
        self.assertFalse(success)
        self.assertIn("numbers", msg)

    def test_not_enough_letters(self):
        success, msg = self.auth._validate_password_format("12345")
        self.assertFalse(success)
        self.assertIn("letters", msg)

    def test_password_with_spaces_in_the_middle(self):
        success, msg = self.auth._validate_password_format("ab  12")
        self.assertFalse(success)

    def test_password_with_spaces_in_the_end(self):
        success, msg = self.auth._validate_password_format("ab12  ")
        self.assertFalse(success)

    def test_password_with_spaces__in_front(self):
        success, msg = self.auth._validate_password_format("  ab12")
        self.assertFalse(success)

    def test_password_too_long(self):
        success, msg = self.auth._validate_password_format("ab12ab12ab12ab12ab12ab12ab12ab12")
        self.assertFalse(success)


class TestLoginEdgeCases(unittest.TestCase):

    def setUp(self):
        self.connection = MagicMock()
        self.storage = MagicMock()
        self.auth = AuthManager(self.storage)

    def test_login_invalid_username(self):
        """_get_validated_username returns invalid → login fails"""
        with patch.object(self.auth, "_get_validated_username", return_value=("", "User not found")):
            username, msg = self.auth.login(self.connection)
            self.assertEqual(username, "")
            self.assertIn("User not found", msg)

    def test_login_invalid_password(self):
        """_prompt_for_password returns weak password → login fails"""
        with patch.object(self.auth, "_get_validated_username", return_value=("bob", "")), \
             patch.object(self.auth, "_prompt_for_password", return_value=("wrong", "")), \
             patch.object(self.storage, "verify_password", return_value=False):

            username, msg = self.auth.login(self.connection)
            self.assertEqual(username, "")
            self.assertIn("Password is not correct", msg)


class TestRegisterEdgeCases(unittest.TestCase):

    def setUp(self):
        self.connection = MagicMock()
        self.storage = MagicMock()
        self.auth = AuthManager(self.storage)

    def test_register_password_invalid(self):
        """Password fails validation → register fails"""
        with patch.object(self.auth, "_get_validated_username", return_value=("alice", "")), \
             patch.object(self.auth, "_prompt_for_password", return_value=("", "Password too weak")):

            username, msg = self.auth.register(self.connection)
            self.assertEqual(username, "")
            self.assertIn("Password too weak", msg)

    def test_register_storage_failure(self):
        """Storage fails to create client → register fails"""
        with patch.object(self.auth, "_get_validated_username", return_value=("alice", "")), \
             patch.object(self.auth, "_prompt_for_password", return_value=("aa11bb", "")), \
             patch.object(self.storage, "create_client", return_value=False):

            username, msg = self.auth.register(self.connection)
            self.assertEqual(username, "")
            self.assertIn("Couldn't add information", msg)

    def test_register_success(self):
        """Normal registration succeeds"""
        with patch.object(self.auth, "_get_validated_username", return_value=("alice", "")), \
             patch.object(self.auth, "_prompt_for_password", return_value=("aa11bb", "")), \
             patch.object(self.storage, "create_client", return_value=True):

            username, msg = self.auth.register(self.connection)
            self.assertEqual(username, "alice")
            self.assertEqual(msg, "")


class TestAuthenticateClientLoop(unittest.TestCase):

    def setUp(self):
        self.connection = MagicMock()
        self.storage = MagicMock()
        self.auth = AuthManager(self.storage)

    def test_empty_command_then_login_success(self):
        """Empty command first, then correct /login"""
        self.connection.receive_from_client.side_effect = ["", "/login"]
        with patch.object(self.auth, "login", return_value=("bob", "")), \
             patch.object(self.auth, "register", return_value=("", "")):

            username = self.auth.authenticate_client(self.connection)
            self.assertEqual(username, "bob")

    def test_unknown_command_then_register_success(self):
        """Unknown command first, then /register"""
        self.connection.receive_from_client.side_effect = ["hello", "/register"]
        with patch.object(self.auth, "login", return_value=("", "")), \
             patch.object(self.auth, "register", return_value=("alice", "")):

            username = self.auth.authenticate_client(self.connection)
            self.assertEqual(username, "alice")

    def test_too_many_arguments(self):
        """Command with too many arguments loops"""
        self.connection.receive_from_client.side_effect = ["login extra", "/login"]
        with patch.object(self.auth, "login", return_value=("bob", "")), \
             patch.object(self.auth, "register", return_value=("", "")):

            username = self.auth.authenticate_client(self.connection)
            self.assertEqual(username, "bob")


class TestGetValidatedUsername(unittest.TestCase):

    def setUp(self):
        self.connection = MagicMock()
        self.storage = MagicMock()
        self.auth = AuthManager(self.storage)

    def test_username_empty(self):
        """Returns error when user enters empty username"""
        self.connection.receive_from_client.return_value = ""
        username, msg = self.auth._get_validated_username(self.connection, must_exist=True)
        self.assertEqual(username, "")
        self.assertIn("haven't entered", msg)

    def test_username_does_not_exist_must_exist(self):
        """Returns error when username must exist but doesn't"""
        self.connection.receive_from_client.return_value = "bob"
        self.storage.client_exists.return_value = False  # simulate username missing
        username, msg = self.auth._get_validated_username(self.connection, must_exist=True)
        self.assertEqual(username, "")
        self.assertIn("doesn't exist", msg)

    def test_username_taken_must_not_exist(self):
        """Returns error when username must NOT exist but is already taken"""
        self.connection.receive_from_client.return_value = "alice"
        self.storage.client_exists.return_value = True  # username taken
        username, msg = self.auth._get_validated_username(self.connection, must_exist=False)
        self.assertEqual(username, "")
        self.assertIn("not available", msg)

    def test_username_available_must_not_exist(self):
        """Returns username successfully when username is available"""
        self.connection.receive_from_client.return_value = "charlie"
        self.storage.client_exists.return_value = False  # username free
        username, msg = self.auth._get_validated_username(self.connection, must_exist=False)
        self.assertEqual(username, "charlie")
        self.assertEqual(msg, "")


if __name__ == "__main__":
    unittest.main()