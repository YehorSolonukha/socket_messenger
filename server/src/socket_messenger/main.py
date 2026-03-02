from socket_messenger.core.server.server_manager import ServerManager


def main():
    serv_manager = ServerManager()
    serv_manager.run()

if __name__ == "__main__":
    main()


