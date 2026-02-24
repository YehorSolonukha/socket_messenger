from socket_messenger.storage.storage_manager import StorageManager
from socket_messenger.network.client_connection import ClientConnection

class AuthManager:
    def __init__(self, storage: StorageManager):
        self._storage = storage

    def authenticate_client(self, connection: ClientConnection) -> str:
        while True:
            connection.send_to_client("Would you like to /login or /register ?")
            command = connection.receive_from_client().strip()

            if not command:
                connection.send_to_client(
                    "Seems like you didn't enter anything, please try again\n"
                )
                continue
            elif len(command.split()) != 1:
                connection.send_to_client(
                    "Too many arguments, should be either '/login' or '/register', nothing more... Please try again\n"
                )
                continue
            elif command == "/login":
                username, description = self.login(connection)
                if not username:
                    connection.send_to_client(description)
                    continue
                break
            elif command == "/register":
                username, description = self.register(connection)
                if not username:
                    connection.send_to_client(description)
                    continue
                break
            else:
                connection.send_to_client("Unknown command... Please try again\n")

        return username


    def login(self, connection) -> tuple[str, str]:
        username, description = self._get_validated_username(connection, must_exist=True)
        if not username:
            return "", description
        
        password, description = self._prompt_for_password(connection)
        if not self._storage.verify_password(username, password):
            description = "Password is not correct"
            return "", description
        
        return username, ""

    def register(self, connection:ClientConnection) -> tuple[str, str]:
        username, description = self._get_validated_username(connection, must_exist=False)
        if not username:
            return "", description

        password, description = self._prompt_for_password(connection)
        if not password:
            return "", description

        # Add client to persistent storage
        success = self._storage.create_client(username, password)
        if not success:
            description = "Couldn't add information to our storage..."
            return "", description

        return username, ""

    def _get_validated_username(
        self, connection: ClientConnection, 
        must_exist: bool, 
    ) -> tuple[str, str]:
        """
        Requests a username from the client and validates it
        """
        connection.send_to_client("Please, enter username")
        username = connection.receive_from_client()

        if not username:
            description = (
                "Sorry, you haven't entered a proper username"
            )
            return "", description

        if not must_exist:
            if self._storage.client_exists(username):
                description = (
                    "Sorry, this username is not available"
                )
                return "", description

        elif must_exist:
            if not self._storage.client_exists(username):
                description = ("Sorry, this username doesn't exist in our database\n")
                return "", description
        return username, ""
            

    def _prompt_for_password(self, connection: ClientConnection) -> tuple[str, str]:
        connection.send_to_client(
            "Please, enter password (at least 2 letters and 2 numbers, at least 5 characters long, max - 15 characters))"
        )
        password = connection.receive_from_client()
        success, descripton = self._validate_password_format(password)
        if not success:
            return "", descripton
        return password, ""

    def _validate_password_format(self, password: str) -> tuple[bool, str]:
        """
        Split into validate password and get_password loop?? to allow for easy unit tests and make it more transparent
        Return a tuple Boolean-Description: str
        learn to use letters/ digits with list comprehensions
        """

        if len(password.split()) > 1:
            description = "Password should be one continuous string, no white spaces"
            return  False, description
        
        if password != password.strip():
            description = "Please, avoid using whitespaces in front or at the end of your password. Password isn't accepted"
            return False, description

        if len(password) > 15:
            description = "Your password is too long"
            return  False, description

        if len(password) < 5:
            description = "Your password is too short"
            return  False, description

        digits = sum(i.isdigit() for i in password)
        letters = sum(i.isalpha() for i in password)

        if digits < 2:
            description = "Password must contain at least 2 numbers"
            return  False, description

        if letters < 2:
            description = "Password must contain at least 2 letters"
            return  False, description

        return True, ""