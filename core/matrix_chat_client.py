import time
import threading
import logging
from typing import Optional, Callable, List, Dict
from simple_client import SimpleMatrixClient
import requests

logger = logging.getLogger(__name__)


class MatrixClient:
    """Оптимізований Matrix клієнт з підтримкою реального часу"""
    
    def __init__(self, homeserver: str):
        """Ініціалізація клієнта"""
        self.homeserver = homeserver.rstrip('/')
        self.client = SimpleMatrixClient(homeserver)
        self.access_token = None
        self.user_id = None
        self.connection_status = "Не підключено"
        
        # Polling
        self.polling_thread = None
        self.polling_active = False
        self.polling_interval = 3  # секунди
        
        # Callbacks
        self.message_callbacks = []
        self.room_callbacks = {}
        
        # Відстеження повідомлень
        self.last_message_ids = {}
        self.processed_messages = set()
        
        # Headers для API запитів
        self.headers = {}
        
    def login(self, username: str, password: str) -> bool:
        """Авторизація користувача"""
        try:
            if self.client.login(username, password):
                self.access_token = self.client.access_token
                self.user_id = self.client.user_id
                self.connection_status = f"Підключено як {username}"
                
                # Встановлюємо headers для API запитів
                if self.access_token:
                    self.headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    }
                
                logger.info(f"Успішна авторизація: {username}")
                return True
            else:
                logger.error("Помилка авторизації")
                return False
        except Exception as e:
            logger.error(f"Помилка авторизації: {e}")
            return False
    
    def get_rooms(self):
        """Отримує список кімнат (для зворотної сумісності)"""
        try:
            url = f"{self.homeserver}/_matrix/client/r0/joined_rooms"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('joined_rooms', [])
            else:
                logger.error(f"Помилка отримання кімнат: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Помилка отримання кімнат: {e}")
            return []
    
    def send_message(self, room_id: str, message: str) -> bool:
        """Відправка повідомлення"""
        if not self.is_connected or not self.client:
            logger.error("Не авторизовано")
            return False
            
        try:
            result = self.client.send_message(room_id, message)
            return result
        except Exception as e:
            logger.error(f"Помилка відправки повідомлення: {e}")
            return False
    
    def get_messages(self, room_id: str, limit: int = 20) -> Optional[List[Dict]]:
        """Отримання повідомлень з кімнати"""
        if not self.is_connected or not self.client:
            logger.error("Не авторизовано")
            return None
            
        try:
            messages = self.client.get_messages(room_id, limit)
            return messages
        except Exception as e:
            logger.error(f"Помилка отримання повідомлень: {e}")
            return None
    
    def add_message_callback(self, callback: Callable):
        """Додає callback для обробки нових повідомлень"""
        self.message_callbacks.append(callback)
        logger.info("Callback для повідомлень додано")
    
    def add_room_callback(self, room_id: str, callback: Callable):
        """Додає callback для конкретної кімнати"""
        self.room_callbacks[room_id] = callback
        logger.info(f"Callback для кімнати {room_id} додано")
    
    def _polling_worker(self):
        """Робочий потік для polling повідомлень"""
        logger.info("Polling worker запущено")
        
        while self.polling_active:
            try:
                # Перевіряємо всі кімнати
                rooms = self.get_rooms()
                if not rooms:
                    time.sleep(self.polling_interval)
                    continue
                
                for room_id in rooms:
                    try:
                        # Отримуємо останні повідомлення
                        messages = self.get_messages(room_id, limit=5)
                        if not messages:
                            continue
                        
                        # Перевіряємо нові повідомлення
                        last_id = self.last_message_ids.get(room_id, "")
                        
                        for message in messages:
                            event_id = message.get('event_id', '')
                            
                            # Якщо це нове повідомлення
                            if event_id and event_id != last_id:
                                if last_id:  # Пропускаємо першу перевірку
                                    # Перевіряємо, чи не обробляли ми це повідомлення
                                    if event_id not in self.processed_messages:
                                        self._process_new_message(room_id, message)
                                        self.processed_messages.add(event_id)
                                
                                # Оновлюємо останній ID
                                self.last_message_ids[room_id] = event_id
                        
                    except Exception as e:
                        logger.error(f"Помилка обробки кімнати {room_id}: {e}")
                        continue
                
                # Чекаємо до наступної перевірки
                time.sleep(self.polling_interval)
                
            except Exception as e:
                logger.error(f"Помилка в polling worker: {e}")
                time.sleep(self.polling_interval * 2)
        
        logger.info("Polling worker зупинено")
    
    def _process_new_message(self, room_id: str, message: Dict):
        """Обробляє нове повідомлення"""
        try:
            # Перевіряємо, чи це текстове повідомлення з правильним текстом
            body = message.get('body', '')
            if not body or body == 'Невідоме повідомлення':
                return  # Пропускаємо повідомлення без тексту
            
            message_data = {
                'room_id': room_id,
                'sender': message.get('sender', 'Невідомий'),
                'body': body,
                'timestamp': message.get('timestamp', 0),
                'event_id': message.get('event_id', 'Невідомий ID')
            }
            
            # Викликаємо тільки загальний callback (без room callback для уникнення задвоєння)
            for callback in self.message_callbacks:
                try:
                    callback(message_data)
                except Exception as e:
                    logger.error(f"Помилка в callback: {e}")
                    
        except Exception as e:
            logger.error(f"Помилка обробки нового повідомлення: {e}")
    
    def start_polling(self, room_id: str = None):
        """Запускає polling для отримання нових повідомлень"""
        if not self.is_connected:
            logger.error("Не авторизовано")
            return False
        
        if self.polling_active:
            logger.warning("Polling вже активний")
            return True
        
        try:
            # Ініціалізуємо останні ID повідомлень
            if room_id:
                rooms_to_check = [room_id]
            else:
                rooms_to_check = self.get_rooms() or []
            
            for rid in rooms_to_check:
                messages = self.get_messages(rid, limit=1)
                if messages:
                    # Беремо ID останнього повідомлення
                    self.last_message_ids[rid] = messages[-1].get('event_id', '')
                    logger.info(f"Ініціалізовано останній ID для кімнати {rid}: {self.last_message_ids[rid]}")
            
            # Запускаємо polling thread
            self.polling_active = True
            self.polling_thread = threading.Thread(target=self._polling_worker, daemon=True)
            self.polling_thread.start()
            
            self.connection_status = "Polling активний"
            logger.info("Polling запущено")
            return True
            
        except Exception as e:
            logger.error(f"Помилка запуску polling: {e}")
            return False
    
    def stop_polling(self):
        """Зупиняє polling"""
        if not self.polling_active:
            logger.info("Polling не був активним")
            return
        
        try:
            self.polling_active = False
            
            if self.polling_thread and self.polling_thread.is_alive():
                self.polling_thread.join(timeout=5)
            
            self.connection_status = "Polling зупинено"
            logger.info("Polling зупинено")
            
        except Exception as e:
            logger.error(f"Помилка зупинки polling: {e}")
    
    def is_authenticated(self):
        """Перевіряє, чи авторизований користувач"""
        return bool(self.access_token and self.user_id)
    
    def is_connected(self):
        """Перевіряє, чи підключений клієнт (для зворотної сумісності)"""
        return self.is_authenticated()
    
    def logout(self):
        """Вихід з системи"""
        try:
            # Зупиняємо polling
            self.stop_polling()
            
            # Вихід з клієнта
            if self.client:
                self.client.logout()
            
            self.is_connected = False
            self.client = None
            self.connection_status = "Відключено"
            logger.info("Вихід з системи виконано")
            
        except Exception as e:
            logger.error(f"Помилка виходу: {e}")
    
    def get_status(self):
        """Отримує статус клієнта"""
        return {
            'is_connected': self.is_connected,
            'is_authenticated': self.is_authenticated(),
            'polling_active': self.polling_active,
            'polling_interval': self.polling_interval,
            'connection_status': self.connection_status,
            'rooms_count': len(self.get_rooms() or []),
            'callbacks_count': len(self.message_callbacks)
        }
    
    def get_user_id(self) -> Optional[str]:
        """Отримує ID користувача"""
        if self.client:
            return self.client.user_id
        return None

    def get_room_info(self, room_id):
        """Отримує інформацію про кімнату (назва, опис)"""
        try:
            url = f"{self.homeserver}/_matrix/client/r0/rooms/{room_id}/state/m.room.name"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Додаємо логування для діагностики
                logger.debug(f"Room {room_id} API response: {data}")
                
                # Назва кімнати може бути в різних місцях залежно від API
                room_name = None
                
                # Спробуємо різні варіанти
                if 'content' in data and 'name' in data['content']:
                    room_name = data['content']['name']
                    logger.debug(f"Found name in content: '{room_name}'")
                elif 'name' in data:
                    room_name = data['name']
                    logger.debug(f"Found name in root: '{room_name}'")
                
                if room_name and room_name.strip():
                    # Якщо є назва, використовуємо її
                    logger.info(f"Found room name for {room_id}: {room_name}")
                    return {
                        'id': room_id,
                        'name': room_name,
                        'display_name': room_name
                    }
                else:
                    # Якщо назви немає або вона порожня, створюємо коротку назву з ID
                    short_id = room_id.split(':')[0][1:]
                    logger.info(f"No room name found for {room_id}, using short ID: {short_id}")
                    return {
                        'id': room_id,
                        'name': short_id,
                        'display_name': f"Кімната {short_id}"
                    }
            else:
                # Якщо назва не знайдена, створюємо коротку назву з ID
                short_id = room_id.split(':')[0][1:]
                logger.info(f"Room name API failed for {room_id} (status: {response.status_code}), using short ID: {short_id}")
                return {
                    'id': room_id,
                    'name': short_id,
                    'display_name': f"Кімната {short_id}"
                }
                
        except Exception as e:
            logger.error(f"Помилка отримання інформації про кімнату {room_id}: {e}")
            short_id = room_id.split(':')[0][1:]
            return {
                'id': room_id,
                'name': short_id,
                'display_name': f"Кімната {short_id}"
            }
    
    def get_rooms_with_names(self):
        """Отримує список кімнат з назвами"""
        try:
            url = f"{self.homeserver}/_matrix/client/r0/joined_rooms"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                room_ids = data.get('joined_rooms', [])
                
                rooms_info = []
                for room_id in room_ids:
                    room_info = self.get_room_info(room_id)
                    rooms_info.append(room_info)
                
                # Сортуємо за назвою
                rooms_info.sort(key=lambda x: x['display_name'].lower())
                return rooms_info
            else:
                logger.error(f"Помилка отримання кімнат: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Помилка отримання кімнат: {e}")
            return []
