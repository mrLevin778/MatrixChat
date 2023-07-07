from matrix_client.client import MatrixClient


class Auth:

    def __init__(self, username, password, homeserver):
        self.username = username
        self.password = password
        self.homeserver = homeserver
        self.client = None

    def authenticate(self):
        client = MatrixClient(self.homeserver)  # connect to Matrix server
        try:
            client.login(username=self.username, password=self.password)  # try auth
            print(f'Connecting to server {self.homeserver} for user {self.username} is OK')
        except Exception as e:
            try:
                # if auth is wrong, try register
                client.register_with_password(username=self.username, password=self.password)
                print(f'Registration and authentication is success!')
            except Exception as e:
                print(f'Error in registration/authentication!')
        return client
