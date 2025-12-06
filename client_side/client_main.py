from client import Client

client = Client()

client.establish_connection()
client.receive_the_menu()
client.talk_to_server()