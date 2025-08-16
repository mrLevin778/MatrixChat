#!/usr/bin/env python3
"""
Тест обробки повідомлень Matrix
"""

import sys
import os

# Додаємо шлях до core директорії
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from simple_client import SimpleMatrixClient

def test_message_processing():
    """Тестуємо обробку повідомлень"""
    
    print("🧪 Тест обробки повідомлень Matrix...")
    
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
    client = SimpleMatrixClient(homeserver)
    
    # Авторизація
    print("🔐 Авторизація...")
    if not client.login(username, password):
        print("❌ Помилка авторизації!")
        return
    
    print("✅ Авторизація успішна!")
    print()
    
    # Тестуємо отримання повідомлень
    print("📥 Тестування обробки повідомлень...")
    messages = client.get_messages(room_id, limit=10)
    
    if messages:
        print(f"✅ Отримано {len(messages)} повідомлень")
        print("\n📋 Деталі повідомлень:")
        
        for i, msg in enumerate(messages, 1):
            print(f"\n   {i}. Повідомлення:")
            print(f"      Event ID: {msg.get('event_id', 'Немає')}")
            print(f"      Sender: {msg.get('sender', 'Немає')}")
            print(f"      Body: {msg.get('body', 'Немає')}")
            print(f"      Timestamp: {msg.get('timestamp', 'Немає')}")
            print(f"      Type: {msg.get('type', 'Немає')}")
            print(f"      Room ID: {msg.get('room_id', 'Немає')}")
            
            # Перевіряємо, чи це правильне повідомлення
            if msg.get('body') and msg.get('body') != 'Невідоме повідомлення':
                print(f"      ✅ Правильне повідомлення")
            else:
                print(f"      ❌ Проблемне повідомлення")
    else:
        print("❌ Не вдалося отримати повідомлення")
    
    # Вихід
    client.logout()
    print("\n👋 Тестування завершено")

if __name__ == "__main__":
    test_message_processing()
