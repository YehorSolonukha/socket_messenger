from enum import Enum

class ClientState(Enum):
    MENU: str = "menu"
    CHAT: str = "chat"
    DISCONNECTED: str = "disconnected"