from enum import Enum


class ClientStates(Enum):
    MENU = "menu"
    CHAT = "chat"
    DISCONNECTED = "disconnected"
