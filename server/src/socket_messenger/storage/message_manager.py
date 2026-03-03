import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class Message:
    def __init__(self, sender: str, receiver: str, content: str, timestamp=None):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = timestamp

class MessageManager:
    def __init__(self):
        # Load credentials from .env
        self.db_params = {
            "host": os.environ.get("DB_HOST"),
            "dbname": os.environ.get("DB_NAME"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD"),
            "port": int(os.environ.get("DB_PORT", 5432)),
            "connect_timeout":5
        }

    def _get_connection(self):
        return psycopg2.connect(**self.db_params)

    def save_message(self, message: Message) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO messages (sender_username, receiver_username, content) 
                        VALUES (%s, %s, %s) RETURNING sent_at;
                        """,
                        (message.sender, message.receiver, message.content)
                    )
                    generated_timestamp = cur.fetchone()[0]
                    message.timestamp = generated_timestamp
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False

    def get_messages_between(self, sender: str, receiver: str) -> list[Message]:
        chat_history = []
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT sender_username, receiver_username, content, sent_at 
                        FROM messages 
                        WHERE (sender_username = %s AND receiver_username = %s) 
                           OR (sender_username = %s AND receiver_username = %s)
                        ORDER BY sent_at ASC;
                        """,
                        (sender, receiver, receiver, sender)
                    )
                    rows = cur.fetchall()
                    for row in rows:
                        msg = Message(
                            sender=row[0], 
                            receiver=row[1], 
                            content=row[2], 
                            timestamp=row[3]
                        )
                        chat_history.append(msg)
        except Exception as e:
            print(f"Error retrieving messages: {e}")
        return chat_history