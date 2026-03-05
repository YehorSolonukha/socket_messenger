import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from socket_messenger.storage.storage_manager import StorageManager


load_dotenv()

class Message:
    def __init__(self, sender: str, receiver: str, content: str, timestamp=None):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = timestamp

class MessageManager:
    def __init__(self, storage_manager: StorageManager):
        self.storage_manager = storage_manager
        

    def save_message(self, message: Message) -> bool:
        try:
            with self.storage_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO messages (sender_username, receiver_username, content) 
                        VALUES (%s, %s, %s) RETURNING sent_at;
                        """,
                        (message.sender, message.receiver, message.content)
                    )
                    now = datetime.now()
                    formatted_time = now.strftime("%m-%d %H:%M")
                    message.timestamp = formatted_time
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False

    def get_messages_between(self, sender: str, receiver: str) -> list[Message]:
        chat_history = []
        try:
            with self.storage_manager.get_connection() as conn:
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