#!/usr/bin/env python3
"""
Скрипт для очищення та оптимізації проекту MatrixChat
"""

import os
import shutil

def cleanup_project():
    """Очищає проект від застарілих файлів"""
    
    print("🧹 Очищення проекту MatrixChat...")
    
    # Файли для видалення
    files_to_remove = [
        'core/realtime_client.py',
        'core/connect_realtime.py', 
        'core/messaging_realtime.py',
        'core/main_realtime.py',
        'core/simple_realtime_client.py',
        'test_realtime.py',
        'test_simple_realtime.py',
        'test_polling.py',
        'test_rooms.py',
        'test_specific_room.py',
        'test_chat.py'
    ]
    
    # Директорії для видалення
    dirs_to_remove = []
    
    # Видаляємо файли
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️  Видалено: {file_path}")
            except Exception as e:
                print(f"❌ Помилка видалення {file_path}: {e}")
    
    # Видаляємо директорії
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"🗑️  Видалено директорію: {dir_path}")
            except Exception as e:
                print(f"❌ Помилка видалення директорії {dir_path}: {e}")
    
    print("\n✅ Очищення завершено!")
    print("\n📁 Поточна структура проекту:")
    
    # Показуємо поточну структуру
    show_project_structure()

def show_project_structure():
    """Показує поточну структуру проекту"""
    
    def print_tree(path, prefix="", is_last=True):
        if not os.path.exists(path):
            return
        
        # Отримуємо список елементів
        items = []
        for item in os.listdir(path):
            if not item.startswith('.') and item not in ['__pycache__', '.git']:
                items.append(item)
        
        items.sort()
        
        for i, item in enumerate(items):
            item_path = os.path.join(path, item)
            is_last_item = i == len(items) - 1
            
            # Визначаємо символ
            if is_last_item:
                symbol = "└── "
                next_prefix = prefix + "    "
            else:
                symbol = "├── "
                next_prefix = prefix + "│   "
            
            # Показуємо елемент
            if os.path.isdir(item_path):
                print(f"{prefix}{symbol}📁 {item}/")
                print_tree(item_path, next_prefix, is_last_item)
            else:
                # Визначаємо іконку для файлу
                if item.endswith('.py'):
                    icon = "🐍"
                elif item.endswith('.md'):
                    icon = "📝"
                elif item.endswith('.txt'):
                    icon = "📄"
                elif item.endswith('.gitignore'):
                    icon = "🚫"
                else:
                    icon = "📄"
                
                print(f"{prefix}{symbol}{icon} {item}")

    print_tree(".")
    
    print("\n🎯 Основні файли:")
    print("   🐍 core/matrix_chat_client.py - основний клієнт")
    print("   🐍 core/simple_client.py - базовий HTTP клієнт")
    print("   🐍 chat_gui.py - графічний інтерфейс")
    print("   🐍 test_matrix_chat.py - тест клієнта")
    print("   📝 README.md - документація")
    print("   📄 requirements.txt - залежності")

def main():
    """Головна функція"""
    print("🚀 MatrixChat - Очищення проекту")
    print("=" * 50)
    
    # Питаємо користувача
    response = input("Видалити застарілі файли? (y/N): ").strip().lower()
    
    if response in ['y', 'yes', 'так']:
        cleanup_project()
    else:
        print("❌ Очищення скасовано")
        show_project_structure()

if __name__ == "__main__":
    main()
