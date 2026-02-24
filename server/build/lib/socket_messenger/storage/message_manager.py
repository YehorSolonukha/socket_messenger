class Message():
    def __init__(self, sender: str, receiver: str, content: str, timestamp):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = timestamp

class MessageManager():
    def save_message(message: Message) -> bool:
        pass

    def get_messages_between(sender: str, receiver: str) -> list[Message]:
        pass