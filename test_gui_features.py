#!/usr/bin/env python3
"""
Тест нових функцій GUI
"""

import sys
import os
import time
from datetime import datetime

# Додаємо шлях до core директорії
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from matrix_chat_client import MatrixClient

def test_gui_features():
    """Тестуємо нові функції GUI"""
    
    print("🧪 Тест нових функцій GUI...")
    
    # Налаштування
    homeserver = "https://matrix.org"
    username = "mrlevin778"
    password = "9Weresnja2015"
    room_id = "!LTWQjiIDDABKYqeBbS:matrix.org"
    
    print(f"📋 Налаштування:")
    print(f"   Homeserver: {homeserver}")
    print(f"   Username: {username}")
    print(f"   Room ID: {room_id}")
    print("=" * 50)
    
    # Створюємо клієнта
    client = MatrixClient(homeserver)
    
    # Авторизація
    print("🔐 Авторизація...")
    if not client.login(username, password):
        print("❌ Помилка авторизації!")
        return
    
    print("✅ Авторизація успішна!")
    print(f"👤 User ID: {client.get_user_id()}")
    print(f"📊 Статус: {client.connection_status}")
    print()
    
    # Тестуємо отримання кімнат
    print("🏠 Тестування отримання кімнат...")
    rooms = client.get_rooms()
    
    if rooms:
        print(f"✅ Знайдено {len(rooms)} кімнат")
        print("📋 Список кімнат:")
        for i, room in enumerate(rooms, 1):
            print(f"   {i}. {room}")
    else:
        print("❌ Кімнати не знайдено")
        client.logout()
        return
    
    print()
    
    # Тестуємо завантаження повідомлень
    print("📥 Тестування завантаження повідомлень...")
    messages = client.get_messages(room_id, limit=20)
    
    if messages:
        print(f"✅ Завантажено {len(messages)} повідомлень")
        print("📋 Останні 5 повідомлень:")
        
        for i, msg in enumerate(messages[-5:], 1):
            sender = msg.get('sender', 'Невідомий')
            body = msg.get('body', 'Невідоме повідомлення')
            timestamp = msg.get('timestamp', 0)
            
            # Форматуємо час
            if timestamp:
                try:
                    dt = datetime.fromtimestamp(timestamp / 1000)
                    time_str = dt.strftime('%H:%M:%S')
                except:
                    time_str = 'Невідомий час'
            else:
                time_str = 'Невідомий час'
            
            print(f"   {i}. [{time_str}] {sender}: {body}")
    else:
        print("❌ Не вдалося завантажити повідомлення")
    
    print()
    
    # Тестуємо відправку повідомлення
    print("📤 Тестування відправки повідомлення...")
    test_message = f"Тест нових функцій GUI! Час: {datetime.now().strftime('%H:%M:%S')}"
    
    if client.send_message(room_id, test_message):
        print("✅ Повідомлення відправлено успішно!")
        print(f"💬 Текст: {test_message}")
    else:
        print("❌ Помилка відправки повідомлення")
    
    print()
    
    # Показуємо статус
    status = client.get_status()
    print("📊 Статус клієнта:")
    print(f"   Підключення: {'✅' if status['is_connected'] else '❌'}")
    print(f"   Авторизація: {'✅' if status['is_authenticated'] else '❌'}")
    print(f"   Статус: {status['connection_status']}")
    print(f"   Кімнати: {status['rooms_count']}")
    print(f"   Callback'и: {status['callbacks_count']}")
    
    # Вихід
    client.logout()
    print("\n👋 Тестування завершено")
    print("\n💡 Тепер можна запустити GUI:")
    print("   python3 chat_gui.py")

if __name__ == "__main__":
    test_gui_features()
