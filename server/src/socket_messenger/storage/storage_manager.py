import os
import psycopg2
import time
from dotenv import load_dotenv

load_dotenv()

class StorageManager:
    def __init__(self):
        # 1. Load credentials
        self.db_params = {
            "host": os.environ.get("DB_HOST"),
            "dbname": os.environ.get("DB_NAME"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD"),
            "port": int(os.environ.get("DB_PORT", 5432)),
            "connect_timeout": 5 # CRITICAL for Azure
        }

        # 2. Automatically initialize schema on startup
        self._wait_for_db()
        self._initialize_schema()

    def _wait_for_db(self):
        """Attempts to connect to the DB in a loop until it's ready."""
        print("Waiting for database to wake up...", flush=True)
        retries = 10
        while retries > 0:
            try:
                conn = self.get_connection()
                conn.close()
                print("✅ Database is online!", flush=True)
                return
            except psycopg2.OperationalError:
                retries -= 1
                print(f"Database not ready yet... ({retries} retries left)", flush=True)
                time.sleep(2)
        raise Exception("Could not connect to database after 20 seconds.")

    def get_connection(self):
        """Helper method to get a fresh database connection."""
        return psycopg2.connect(**self.db_params)

    def _initialize_schema(self):
        """Creates the tables if they do not exist in the database."""
        # Use a raw string (r"") to avoid escape character issues
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """
        
        messages_table_sql = """
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender_username VARCHAR(50) REFERENCES users(username) ON DELETE CASCADE,
            receiver_username VARCHAR(50) REFERENCES users(username) ON DELETE CASCADE,
            content TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        conn = None
        try:
            print("Checking/Initializing database schema...", flush=True)
            conn = self.get_connection()
            # Set autocommit to True so we don't have to manually commit DDL commands
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(users_table_sql)
                cur.execute(messages_table_sql)
            print("✅ Database schema is ready.", flush=True)
        except Exception as e:
            print(f"❌ Failed to initialize schema: {e}", flush=True)
            # You might want to raise the error here to stop the server from starting
            # without a working database connection.
            raise e
        finally:
            if conn:
                conn.close()

    # AUTHENTICATION
    def create_client(self, username: str, password: str) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (username, password) VALUES (%s, %s);", 
                        (username, password)
                    )
            return True
        except Exception as e:
            print(f"Database error during registration: {e}")
            return False

    def client_exists(self, target_username: str) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM users WHERE username = %s;", (target_username,))
                    return cur.fetchone() is not None
        except Exception as e:
            print(f"Error checking client existence: {e}")
            return False

    def verify_password(self, target_username: str, target_password: str) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT password FROM users WHERE username = %s;", (target_username,))
                    result = cur.fetchone()
                    if result and result[0] == target_password:
                        return True
            return False
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False