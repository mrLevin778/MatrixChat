from matrix_client.client import MatrixClient


class Connect:

    def __init__(self, homeserver):
        self.homeserver = homeserver
        self.client = None

    def connect(self, username, password):
        self.client = MatrixClient(self.homeserver)  # connect to Matrix server
        try:
            self.client.login(username=username, password=password)  # try auth
            print(f'Connecting to server {self.homeserver} for user {username} is OK')
        except Exception as e:
            print(f'Authentication is failed! Error {e}')
        return self.client

    def get_rooms(self):
        if self.client:
            rooms = self.client.get_rooms()
            return rooms
        else:
            print(f'Rooms getting is failed! Maybe you may login?')

