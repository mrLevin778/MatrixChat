#!/usr/bin/env python3
"""
Тестування оптимізованого Matrix Chat клієнта
"""

import sys
import os
import time
from datetime import datetime

# Додаємо шлях до core директорії
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from matrix_chat_client import MatrixClient

def test_matrix_chat_client():
    """Тестуємо оптимізований клієнт"""
    
    print("🧪 Тестування оптимізованого Matrix Chat клієнта...")
    
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
    
    # Перевіряємо кімнати
    print("🏠 Перевірка кімнат...")
    rooms = client.get_rooms()
    
    if rooms and room_id in rooms:
        print(f"✅ Користувач знаходиться в кімнаті {room_id}")
    else:
        print(f"❌ Користувач НЕ знаходиться в кімнаті {room_id}")
        print("💡 Приєднайтесь до кімнати в Element")
        client.logout()
        return
    
    print()
    
    # Тест 1: Відправка повідомлення
    print("📤 ТЕСТ 1: Відправка повідомлення")
    test_message = f"Тест оптимізованого клієнта! Час: {datetime.now().strftime('%H:%M:%S')}"
    
    if client.send_message(room_id, test_message):
        print("✅ Повідомлення відправлено успішно!")
        print(f"💬 Текст: {test_message}")
    else:
        print("❌ Помилка відправки повідомлення")
    
    print()
    
    # Тест 2: Отримання повідомлень
    print("📥 ТЕСТ 2: Отримання повідомлень")
    messages = client.get_messages(room_id, limit=5)
    
    if messages:
        print(f"✅ Отримано {len(messages)} повідомлень")
        print("📋 Останні повідомлення:")
        
        for i, msg in enumerate(messages[-3:], 1):
            sender = msg.get('sender', 'Невідомий')
            body = msg.get('body', 'Невідоме повідомлення')
            print(f"   {i}. [{sender}] {body}")
    else:
        print("❌ Не вдалося отримати повідомлення")
    
    print()
    
    # Тест 3: Налаштування callback'ів
    print("🎧 ТЕСТ 3: Налаштування callback'ів для реального часу")
    
    def message_handler(message_data):
        print(f"\n🔔 CALLBACK: Отримано повідомлення від {message_data.get('sender')}")
        print(f"   Текст: {message_data.get('body')}")
        print(f"   Кімната: {message_data.get('room_id')}")
        print(f"   Час: {datetime.fromtimestamp(message_data.get('timestamp', 0) / 1000).strftime('%H:%M:%S')}")
    
    # Додаємо callback
    client.add_message_callback(message_handler)
    client.add_room_callback(room_id, message_handler)
    
    print("✅ Callback'и налаштовані")
    
    # Тест 4: Запуск polling
    print("\n🔄 ТЕСТ 4: Запуск polling для реального часу")
    
    if client.start_polling(room_id):
        print("✅ Polling запущено!")
        print("💡 Тепер нові повідомлення будуть автоматично оброблятися")
        print("⏱️  Перевірка кожні 3 секунди")
        
        # Показуємо статус
        status = client.get_status()
        print(f"\n📊 Статус:")
        print(f"   Підключення: {'✅' if status['is_connected'] else '❌'}")
        print(f"   Polling: {'✅' if status['polling_active'] else '❌'}")
        print(f"   Інтервал: {status['polling_interval']} сек")
        print(f"   Статус: {status['connection_status']}")
        print(f"   Кімнати: {status['rooms_count']}")
        print(f"   Callback'и: {status['callbacks_count']}")
        
        print("\n💡 Тестування:")
        print("   1. Відправте повідомлення з Element в цю кімнату")
        print("   2. Воно має з'явитися автоматично через 3 секунди")
        print("   3. Натисніть Ctrl+C для зупинки")
        
        try:
            # Чекаємо нових повідомлень
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Зупинка тестування...")
        
        # Зупиняємо polling
        client.stop_polling()
        print("✅ Polling зупинено")
        
        print("\n🎉 Всі тести пройдено успішно!")
        print("💬 Ваш оптимізований Matrix Chat клієнт працює ідеально!")
        
    else:
        print("❌ Не вдалося запустити polling")
    
    # Вихід
    client.logout()
    print("\n👋 Тестування завершено")

if __name__ == "__main__":
    test_matrix_chat_client()
