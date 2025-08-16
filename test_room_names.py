#!/usr/bin/env python3
"""
Тест функцій отримання назв кімнат
"""

import sys
import os

# Додаємо шлях до core директорії
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from matrix_chat_client import MatrixClient

def test_room_names():
    """Тестуємо отримання назв кімнат"""
    
    print("🧪 Тест функцій отримання назв кімнат...")
    
    # Налаштування
    homeserver = "https://matrix.org"
    username = "mrlevin778"
    password = "9Weresnja2015"
    
    print(f"📋 Налаштування:")
    print(f"   Homeserver: {homeserver}")
    print(f"   Username: {username}")
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
    print(f"🔑 Access Token: {'✅' if client.access_token else '❌'}")
    print(f"📋 Headers: {'✅' if client.headers else '❌'}")
    print()
    
    # Тестуємо отримання кімнат з назвами
    print("🏠 Тестування отримання кімнат з назвами...")
    rooms_info = client.get_rooms_with_names()
    
    if rooms_info:
        print(f"✅ Знайдено {len(rooms_info)} кімнат")
        print("📋 Детальна інформація про кімнати:")
        print("-" * 80)
        
        for i, room in enumerate(rooms_info, 1):
            print(f"{i:2d}. ID: {room['id']}")
            print(f"    Назва: {room['name']}")
            print(f"    Відображення: {room['display_name']}")
            print()
    else:
        print("❌ Кімнати не знайдено")
        client.logout()
        return
    
    print()
    
    # Тестуємо отримання інформації про конкретну кімнату
    print("🔍 Тестування отримання інформації про конкретну кімнату...")
    test_room_id = rooms_info[0]['id']
    room_info = client.get_room_info(test_room_id)
    
    print(f"📋 Кімната: {test_room_id}")
    print(f"   Назва: {room_info['name']}")
    print(f"   Відображення: {room_info['display_name']}")
    print()
    
    # Показуємо статус
    print("📊 Статус клієнта:")
    print(f"   Підключення: ✅")
    print(f"   Авторизація: ✅")
    print(f"   Статус: {client.connection_status}")
    print(f"   Кімнати: {len(rooms_info)}")
    print(f"   Headers: {'✅' if client.headers else '❌'}")
    
    # Вихід
    client.logout()
    print("\n👋 Тестування завершено")
    print("\n💡 Тепер можна запустити покращений GUI:")
    print("   python3 chat_gui.py")

if __name__ == "__main__":
    test_room_names()
