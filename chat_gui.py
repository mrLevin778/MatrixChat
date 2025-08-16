#!/usr/bin/env python3
"""
Matrix Chat GUI - простий інтерфейс для чату
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
import threading
import time
from datetime import datetime

# Додаємо шлях до core директорії
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from matrix_chat_client import MatrixClient

class MatrixChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Matrix Chat")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Matrix клієнт
        self.matrix_client = None
        self.current_room = None
        
        # Налаштування з config.py
        try:
            from config import MATRIX_CONFIG
            self.config = MATRIX_CONFIG
        except ImportError:
            messagebox.showerror("Помилка", "Файл config.py не знайдено!")
            sys.exit(1)
        
        # Створюємо інтерфейс
        self.create_widgets()
        
        # Автоматичне підключення
        self.connect_to_matrix()
    
    def create_widgets(self):
        """Створює віджети інтерфейсу"""
        
        # Головний фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Налаштування grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Matrix Chat", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Інформація про користувача
        user_frame = ttk.LabelFrame(main_frame, text="Користувач", padding="5")
        user_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        user_frame.columnconfigure(1, weight=1)
        
        self.user_info_label = ttk.Label(user_frame, text="Не авторизовано", foreground="red")
        self.user_info_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        # Статус підключення
        self.status_label = ttk.Label(main_frame, text="Статус: Не підключено", foreground="red")
        self.status_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Вибір кімнати
        room_frame = ttk.LabelFrame(main_frame, text="Кімната", padding="5")
        room_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        room_frame.columnconfigure(1, weight=1)
        
        ttk.Label(room_frame, text="Кімната:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(room_frame, textvariable=self.room_var, state="readonly", width=40)
        self.room_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.room_combo.bind("<<ComboboxSelected>>", self.on_room_selected)
        
        ttk.Button(room_frame, text="Оновити", command=self.refresh_rooms).grid(row=0, column=2)
        
        # Чат
        chat_frame = ttk.LabelFrame(main_frame, text="Чат", padding="5")
        chat_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Поле чату (збільшене) з кольоровим форматуванням
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame, 
            height=20, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#000000",  # Чорний фон
            fg="#ffffff",  # Білий основний текст
            insertbackground="#ffffff"  # Білий курсор
        )
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Налаштовуємо теги для кольорів (темна тема)
        self.chat_text.tag_configure("timestamp", foreground="#888888", font=("Consolas", 9))  # Сірий час
        self.chat_text.tag_configure("sender", foreground="#00aaff", font=("Consolas", 10, "bold"))  # Синій відправник
        self.chat_text.tag_configure("message", foreground="#ffffff", font=("Consolas", 10))  # Білий текст
        self.chat_text.tag_configure("system", foreground="#00ff88", font=("Consolas", 9, "italic"))  # Зелений системний
        self.chat_text.tag_configure("error", foreground="#ff4444", font=("Consolas", 9, "bold"))  # Червоний помилка
        
        # Поле введення повідомлення
        input_frame = ttk.Frame(chat_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(input_frame, textvariable=self.message_var, font=("Consolas", 10))
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.message_entry.bind("<Return>", self.send_message)
        
        # Стилізуємо поле введення для темної теми
        style = ttk.Style()
        style.configure('Dark.TEntry', fieldbackground='#333333', foreground='#ffffff')
        self.message_entry.configure(style='Dark.TEntry')
        
        ttk.Button(input_frame, text="Відправити", command=self.send_message).grid(row=0, column=1)
        
        # Сервісне поле (зменшене)
        service_frame = ttk.LabelFrame(main_frame, text="Сервісна інформація", padding="5")
        service_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        service_frame.columnconfigure(0, weight=1)
        service_frame.rowconfigure(0, weight=1)
        
        # Сервісне поле (зменшене) з темною темою
        self.service_text = scrolledtext.ScrolledText(
            service_frame, 
            height=6, 
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#1a1a1a",  # Темно-сірий фон
            fg="#cccccc",  # Світло-сірий текст
            insertbackground="#ffffff"  # Білий курсор
        )
        self.service_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Кнопки керування
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Підключитися", command=self.connect_to_matrix).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Відключитися", command=self.disconnect_from_matrix).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Очистити чат", command=self.clear_chat).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(button_frame, text="Очистити сервіс", command=self.clear_service).grid(row=0, column=3, padx=(0, 5))
    
    def log_service(self, message):
        """Додає повідомлення в сервісне поле"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.service_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.service_text.see(tk.END)
    
    def log_chat(self, message):
        """Додає повідомлення в чат (для зворотної сумісності)"""
        self.chat_text.insert(tk.END, f"{message}\n")
        self.chat_text.see(tk.END)
    
    def update_user_info(self):
        """Оновлює інформацію про користувача"""
        if self.matrix_client and self.matrix_client.is_authenticated():
            user_id = self.matrix_client.get_user_id()
            if user_id:
                self.user_info_label.config(
                    text=f"👤 {user_id} | 🏠 {len(self.matrix_client.get_rooms() or [])} кімнат",
                    foreground="green"
                )
            else:
                self.user_info_label.config(text="Авторизовано", foreground="blue")
        else:
            self.user_info_label.config(text="Не авторизовано", foreground="red")
    
    def connect_to_matrix(self):
        """Підключається до Matrix сервера"""
        try:
            self.log_service("Підключення до Matrix сервера...")
            
            # Створюємо клієнта
            self.matrix_client = MatrixClient(self.config['homeserver'])
            
            # Авторизація
            if self.matrix_client.login(self.config['username'], self.config['password']):
                self.log_service("Авторизація успішна!")
                self.update_status("Підключено", "green")
                self.update_user_info()
                
                # Отримуємо кімнати
                self.refresh_rooms()
                
                # Запускаємо polling
                self.matrix_client.add_message_callback(self.on_new_message)
                if self.matrix_client.start_polling():
                    self.log_service("Polling запущено - очікуємо нових повідомлень")
                else:
                    self.log_service("Помилка запуску polling")
                
            else:
                self.log_service("Помилка авторизації!")
                self.update_status("Помилка авторизації", "red")
                
        except Exception as e:
            self.log_service(f"Помилка підключення: {e}")
            self.update_status(f"Помилка: {str(e)}", "red")
    
    def disconnect_from_matrix(self):
        """Відключається від Matrix сервера"""
        if self.matrix_client:
            self.matrix_client.logout()
            self.matrix_client = None
            self.update_status("Відключено", "red")
            self.update_user_info()
            self.log_service("Відключено від Matrix сервера")
            
            # Очищаємо кімнати
            self.room_combo['values'] = []
            self.room_var.set("")
            self.current_room = None
            
            # Очищаємо чат
            self.clear_chat()
    
    def refresh_rooms(self):
        """Оновлює список кімнат"""
        if not self.matrix_client or not self.matrix_client.is_authenticated():
            self.log_service("Не підключено до сервера")
            return
        
        try:
            rooms_info = self.matrix_client.get_rooms_with_names()
            if rooms_info:
                # Створюємо список для відображення (назва + ID)
                display_list = []
                self.rooms_dict = {}  # Словник для збереження mapping назва -> ID
                
                for room in rooms_info:
                    display_name = room['display_name']
                    room_id = room['id']
                    display_list.append(display_name)
                    self.rooms_dict[display_name] = room_id
                
                self.room_combo['values'] = display_list
                self.log_service(f"Знайдено {len(rooms_info)} кімнат")
                self.update_user_info()
                
                # Встановлюємо поточну кімнату з config
                current_room_id = self.config['room_id']
                for room in rooms_info:
                    if room['id'] == current_room_id:
                        self.room_var.set(room['display_name'])
                        self.on_room_selected()
                        break
                else:
                    # Якщо поточна кімната не знайдена, вибираємо першу
                    if display_list:
                        self.room_var.set(display_list[0])
                        self.on_room_selected()
            else:
                self.log_service("Кімнати не знайдено")
                
        except Exception as e:
            self.log_service(f"Помилка отримання кімнат: {e}")
    
    def on_room_selected(self, event=None):
        """Обробляє вибір кімнати"""
        display_name = self.room_var.get()
        if not display_name or not hasattr(self, 'rooms_dict'):
            return
        
        # Отримуємо ID кімнати з назви
        room_id = self.rooms_dict.get(display_name)
        if not room_id:
            return
        
        self.current_room = room_id
        self.current_room_name = display_name
        self.log_service(f"Вибрано кімнату: {display_name} ({room_id})")
        
        # Очищаємо чат перед завантаженням нових повідомлень
        self.clear_chat()
        
        # Отримуємо повідомлення
        self.load_messages()
    
    def load_messages(self):
        """Завантажує повідомлення з кімнати"""
        if not self.current_room or not self.matrix_client:
            return
        
        try:
            self.log_service(f"Завантаження повідомлень з кімнати {self.current_room_name}...")
            messages = self.matrix_client.get_messages(self.current_room, limit=20)
            if messages:
                self.log_service(f"Завантажено {len(messages)} повідомлень")
                
                # Показуємо повідомлення в чаті
                for msg in messages:
                    sender = msg.get('sender', 'Невідомий')
                    body = msg.get('body', 'Невідоме повідомлення')
                    timestamp = msg.get('timestamp', 0)
                    
                    if body and body != 'Невідоме повідомлення':
                        # Форматуємо час
                        if timestamp:
                            try:
                                dt = datetime.fromtimestamp(timestamp / 1000)
                                time_str = dt.strftime('%H:%M:%S')
                            except:
                                time_str = 'Невідомий час'
                        else:
                            time_str = 'Невідомий час'
                        
                        # Показуємо повідомлення з кольоровим форматуванням
                        self.log_chat_formatted(time_str, sender, body)
            else:
                self.log_service("Повідомлення не знайдено")
                
        except Exception as e:
            self.log_service(f"Помилка завантаження повідомлень: {e}")
    
    def log_chat_formatted(self, timestamp, sender, message):
        """Додає повідомлення в чат з кольоровим форматуванням"""
        self.chat_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_text.insert(tk.END, f"{sender}: ", "sender")
        self.chat_text.insert(tk.END, f"{message}\n", "message")
        self.chat_text.see(tk.END)
    
    def log_chat(self, message):
        """Додає повідомлення в чат (для зворотної сумісності)"""
        self.chat_text.insert(tk.END, f"{message}\n")
        self.chat_text.see(tk.END)
    
    def send_message(self, event=None):
        """Відправляє повідомлення"""
        if not self.current_room or not self.matrix_client:
            messagebox.showwarning("Попередження", "Виберіть кімнату та підключіться до сервера")
            return
        
        message = self.message_var.get().strip()
        if not message:
            return
        
        try:
            if self.matrix_client.send_message(self.current_room, message):
                self.log_service("Повідомлення відправлено")
                self.message_var.set("")  # Очищаємо поле
            else:
                self.log_service("Помилка відправки повідомлення")
                
        except Exception as e:
            self.log_service(f"Помилка відправки: {e}")
    
    def on_new_message(self, message_data):
        """Обробляє нове повідомлення"""
        room_id = message_data.get('room_id', '')
        sender = message_data.get('sender', 'Невідомий')
        body = message_data.get('body', '')
        timestamp = message_data.get('timestamp', 0)
        
        # Логуємо в сервісне поле
        if timestamp:
            try:
                dt = datetime.fromtimestamp(timestamp / 1000)
                time_str = dt.strftime('%H:%M:%S')
            except:
                time_str = 'Невідомий час'
        else:
            time_str = 'Невідомий час'
        
        self.log_service(f"Нове повідомлення [{time_str}] {sender}: {body}")
        
        # Показуємо в чаті тільки якщо це поточна кімната
        if room_id == self.current_room and body:
            self.log_chat_formatted(time_str, sender, body)
    
    def update_status(self, text, color):
        """Оновлює статус підключення"""
        self.status_label.config(text=f"Статус: {text}", foreground=color)
    
    def clear_chat(self):
        """Очищає поле чату"""
        self.chat_text.delete(1.0, tk.END)
        self.log_service("Чат очищено")
    
    def clear_service(self):
        """Очищає сервісне поле"""
        self.service_text.delete(1.0, tk.END)
    
    def on_closing(self):
        """Обробляє закриття програми"""
        if self.matrix_client:
            self.disconnect_from_matrix()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MatrixChatGUI(root)
    
    # Обробник закриття
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Запуск GUI
    root.mainloop()

if __name__ == "__main__":
    main()
