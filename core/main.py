from connect import Connect
from messaging import Messaging

homeserver = 'matrix_server_url'
username = 'username'
password = 'password'

# connect to Matrix server
connection = Connect(homeserver=homeserver)
client = connection.connect(username=username, password=password)

# create Messaging object and receive it to client object
messaging = Messaging(client=client)

# use messaging methods
messaging.send_message("room_id", "Hello, Matrix!")
messaging.get_messages("room_id", limit=5)
messaging.handle_messages("room_id")

# stop event listener
client.stop_listener_thread()
