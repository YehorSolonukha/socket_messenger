import psycopg2
from psycopg2.errors import UniqueViolation

class StorageManager:
    def __init__(self):
        # Store your database credentials here. 
        # (In a real app, you'd load these from a .env file!)
        self.db_params = {
            "host": "database",
            "dbname": "postgres",
            "user": "postgres",
            "password": "password",
            "port": 5432
        }

    def _get_connection(self):
        """Helper method to get a fresh database connection."""
        return psycopg2.connect(**self.db_params)

    # AUTHENTICATION
    def create_client(self, username: str, password: str) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # %s is used to prevent SQL Injection attacks
                    cur.execute(
                        "INSERT INTO users (username, password) VALUES (%s, %s);", 
                        (username, password)
                    )
                # The 'with conn:' block automatically COMMITs the transaction here
            return True
        except UniqueViolation:
            # The database caught a duplicate username because of our UNIQUE constraint!
            return False
        except Exception as e:
            print(f"Database error during registration: {e}")
            return False

    def client_exists(self, target_username: str) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # SELECT 1 is a fast way to check if a row exists without fetching all data
                cur.execute("SELECT 1 FROM users WHERE username = %s;", (target_username,))
                
                # If fetchone() returns data, the user exists. If it returns None, they don't.
                return cur.fetchone() is not None

    def verify_password(self, target_username: str, target_password: str) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT password FROM users WHERE username = %s;", (target_username,))
                result = cur.fetchone()
                
                # result[0] is the password from the database
                if result and result[0] == target_password:
                    return True
        return False