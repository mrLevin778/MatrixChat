from matrix_client.client import MatrixClient


class Messaging:

    def __init__(self, homeserver):
        self.homeserver = homeserver
        self.client = None

    def connect(self, username, password):
        client = MatrixClient(self.homeserver)  # connect to Matrix server
        try:
            client.login(username=username, password=password)  # try auth
            print(f'Connecting to server {self.homeserver} for user {username} is OK')
        except Exception as e:
            try:
                # if auth is wrong, try register
                client.register_with_password(username=username, password=password)
                print(f'Registration and authentication is success!')
            except Exception as e:
                print(f'Error in registration/authentication!')
        return self.client

    def send_message(self, room_id, message):
        if self.client:
            room = self.client.rooms[room_id]
            room.send_text(message)
            print(f'Message sended!')
        else:
            print(f'Message is not sended!')
