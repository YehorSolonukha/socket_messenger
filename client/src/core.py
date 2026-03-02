class Core():
    def __init__(self, network, ui):
        self.network = network
        self.ui = ui
        self.running = True

    def on_user_input(self, message: str):
        if not self.running:
            return
        
        if message:
            self.network.send_to_server(message)

    def on_server_message(self, message: str):
        if not self.running:
            return
        
        if not message:
            self.ui.display("Server disconnected.")
            self.stop()
        else:
            self.ui.display(message)

    def stop(self):
        if self.running == False:
            return
        
        self.network.close_server_connection()
        self.running = False