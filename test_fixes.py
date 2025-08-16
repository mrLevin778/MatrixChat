#!/usr/bin/env python3
"""
Тест виправлень проблем з задвоєнням та повторним оброблянням
"""

import sys
import os
import time
from datetime import datetime

# Додаємо шлях до core директорії
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from matrix_chat_client import MatrixClient

def test_fixes():
    """Тестуємо виправлення"""
    
    print("🧪 Тест виправлень проблем...")
    
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
    print()
    
    # Тестуємо callback'и
    print("🎧 Тестування callback'ів...")
    
    message_count = 0
    processed_messages = set()
    
    def message_handler(message_data):
        nonlocal message_count
        message_count += 1
        
        event_id = message_data.get('event_id', '')
        sender = message_data.get('sender', 'Невідомий')
        body = message_data.get('body', 'Невідоме повідомлення')
        
        print(f"\n🔔 CALLBACK #{message_count}: {event_id[:20]}...")
        print(f"   Від: {sender}")
        print(f"   Текст: {body}")
        
        # Перевіряємо задвоєння
        if event_id in processed_messages:
            print(f"   ❌ ДУБЛІКАТ! Це повідомлення вже оброблялося")
        else:
            print(f"   ✅ НОВЕ повідомлення")
            processed_messages.add(event_id)
    
    # Додаємо callback
    client.add_message_callback(message_handler)
    print("✅ Callback додано")
    
    # Запускаємо polling
    print("\n🔄 Запуск polling...")
    if client.start_polling(room_id):
        print("✅ Polling запущено!")
        print("💡 Очікуємо нових повідомлень...")
        print("⏱️  Тест триватиме 15 секунд")
        
        start_time = time.time()
        while time.time() - start_time < 15:
            time.sleep(1)
            if message_count > 0:
                print(f"📊 Оброблено повідомлень: {message_count}")
                print(f"📊 Унікальних ID: {len(processed_messages)}")
        
        # Зупиняємо polling
        client.stop_polling()
        print("✅ Polling зупинено")
        
        # Аналіз результатів
        print(f"\n📊 РЕЗУЛЬТАТИ:")
        print(f"   Загальна кількість callback'ів: {message_count}")
        print(f"   Унікальних повідомлень: {len(processed_messages)}")
        
        if message_count == len(processed_messages):
            print("   ✅ ЗАДВОЄННЯ ВИПРАВЛЕНО!")
        else:
            print("   ❌ Ще є задвоєння")
        
        if message_count > 0:
            print("   ✅ НОВІ ПОВІДОМЛЕННЯ ОБРОБЛЯЮТЬСЯ!")
        else:
            print("   ❌ Повідомлення не обробляються")
        
    else:
        print("❌ Не вдалося запустити polling")
    
    # Вихід
    client.logout()
    print("\n👋 Тестування завершено")

if __name__ == "__main__":
    test_fixes()
