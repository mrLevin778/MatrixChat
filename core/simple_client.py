import requests
import json
import logging
import time

logger = logging.getLogger(__name__)


class SimpleMatrixClient:
    """Простий Matrix клієнт на основі requests"""
    
    def __init__(self, homeserver):
        self.homeserver = homeserver.rstrip('/')
        self.access_token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MatrixChat/1.0',
            'Content-Type': 'application/json'
        })
    
    def login(self, username, password):
        """Авторизація користувача"""
        try:
            logger.info(f"Авторизація користувача {username}...")
            
            # Endpoint для авторизації
            login_url = f"{self.homeserver}/_matrix/client/r0/login"
            
            login_data = {
                "type": "m.login.password",
                "identifier": {
                    "type": "m.id.user",
                    "user": username
                },
                "password": password,
                "device_id": f"MatrixChat_{int(time.time())}"
            }
            
            response = self.session.post(login_url, json=login_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Оновлюємо заголовки з токеном
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                logger.info(f"Успішна авторизація: {self.user_id}")
                return True
            else:
                logger.error(f"Помилка авторизації: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Помилка підключення: {e}")
            return False
    
    def get_rooms(self):
        """Отримання списку кімнат"""
        try:
            if not self.access_token:
                logger.error("Не авторизовано")
                return None
            
            # Endpoint для отримання кімнат
            rooms_url = f"{self.homeserver}/_matrix/client/r0/joined_rooms"
            response = self.session.get(rooms_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                rooms = data.get('joined_rooms', [])
                logger.info(f"Знайдено {len(rooms)} кімнат")
                return rooms
            else:
                logger.error(f"Помилка отримання кімнат: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Помилка отримання кімнат: {e}")
            return None
    
    def send_message(self, room_id, message):
        """Відправка повідомлення"""
        try:
            if not self.access_token:
                logger.error("Не авторизовано")
                return False
            
            # Endpoint для відправки повідомлення
            send_url = f"{self.homeserver}/_matrix/client/r0/rooms/{room_id}/send/m.room.message"
            
            message_data = {
                "msgtype": "m.text",
                "body": message
            }
            
            response = self.session.post(send_url, json=message_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                event_id = data.get('event_id')
                logger.info(f"Повідомлення відправлено: {event_id}")
                return True
            else:
                logger.error(f"Помилка відправки: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Помилка відправки повідомлення: {e}")
            return False
    
    def get_messages(self, room_id, limit=10):
        """Отримання повідомлень з кімнати"""
        try:
            if not self.access_token:
                logger.error("Не авторизовано")
                return None
            
            # Endpoint для отримання повідомлень
            messages_url = f"{self.homeserver}/_matrix/client/r0/rooms/{room_id}/messages"
            params = {
                'limit': limit,
                'dir': 'b'  # backwards (новіші повідомлення)
            }
            
            response = self.session.get(messages_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                raw_messages = data.get('chunk', [])
                
                # Обробляємо повідомлення в правильний формат
                processed_messages = []
                for msg in raw_messages:
                    # Перевіряємо, чи це текстове повідомлення
                    if msg.get('type') == 'm.room.message':
                        content = msg.get('content', {})
                        if content.get('msgtype') == 'm.text':
                            processed_message = {
                                'event_id': msg.get('event_id', ''),
                                'sender': msg.get('sender', ''),
                                'body': content.get('body', ''),
                                'timestamp': msg.get('origin_server_ts', 0),
                                'type': msg.get('type', ''),
                                'room_id': room_id
                            }
                            processed_messages.append(processed_message)
                
                logger.info(f"Отримано {len(processed_messages)} текстових повідомлень з {len(raw_messages)} загальних")
                return processed_messages
            else:
                logger.error(f"Помилка отримання повідомлень: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Помилка отримання повідомлень: {e}")
            return None
    
    def is_authenticated(self):
        """Перевірка авторизації"""
        return self.access_token is not None and self.user_id is not None
    
    def logout(self):
        """Вихід з системи"""
        try:
            if self.access_token:
                logout_url = f"{self.homeserver}/_matrix/client/r0/logout"
                self.session.post(logout_url, timeout=30)
                
            self.access_token = None
            self.user_id = None
            logger.info("Вихід з системи виконано")
            
        except Exception as e:
            logger.error(f"Помилка виходу: {e}")
