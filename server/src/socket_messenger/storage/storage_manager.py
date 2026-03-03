import os
import psycopg2
from psycopg2.errors import UniqueViolation
from dotenv import load_dotenv

load_dotenv()

class StorageManager:
    def __init__(self):
        # Load credentials from .env
        self.db_params = {
            "host": os.environ.get("DB_HOST"),
            "dbname": os.environ.get("DB_NAME"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD"),
            "port": int(os.environ.get("DB_PORT", 5432)),
            "connect_timeout":5,
            "sslmode": "require"
        }

    def _get_connection(self):
        """Helper method to get a fresh database connection."""
        return psycopg2.connect(**self.db_params)

    # AUTHENTICATION
    def create_client(self, username: str, password: str) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (username, password) VALUES (%s, %s);", 
                        (username, password)
                    )
            return True
        except UniqueViolation:
            return False
        except Exception as e:
            print(f"Database error during registration: {e}")
            return False

    def client_exists(self, target_username: str) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM users WHERE username = %s;", (target_username,))
                    return cur.fetchone() is not None
        except Exception as e:
            print(f"Error checking client existence: {e}")
            return False

    def verify_password(self, target_username: str, target_password: str) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT password FROM users WHERE username = %s;", (target_username,))
                    result = cur.fetchone()
                    if result and result[0] == target_password:
                        return True
            return False
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False