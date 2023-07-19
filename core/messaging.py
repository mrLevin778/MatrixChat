from matrix_client.client import MatrixClient


class Messaging:

    def __init__(self, client):
        self.client = client

    def send_message(self, room_id, message):
        if self.client:
            room = self.client.rooms[room_id]
            room.send_text(message)
            print(f'Message sended!')
        else:
            print(f'Message is not sended!')

    def get_messages(self, room_id, limit=None):
        if self.client:
            room = self.client.rooms[room_id]
            messages = room.get_messages(limit=limit)
            return messages
        else:
            print(f'Getting messages is failed')

    def handle_messages(self, room_id):
        if self.client:
            room = self.client.rooms[room_id]
            room.add_listener(self.on_message)  # adding event handler for messages
            self.client.start_listener_thread()  # start event listener
        else:
            print(f'Failed message handling')

    def on_message(self, room, event):
        print(f'Messsage in room {room.room_id}: {event["content"]["body"]}')
