# Приклад конфігурації для тестування
# Скопіюйте цей файл як config.py та налаштуйте під себе

MATRIX_CONFIG = {
    'homeserver': 'https://matrix.org',  # Публічний Matrix сервер для тестування
    'username': 'test_user_example',     # Замініть на ваш username
    'password': 'test_password_example', # Замініть на ваш пароль
    'room_id': '!test:matrix.org'        # ID тестової кімнати
}

# Для тестування на matrix.org:
# 1. Створіть акаунт на https://app.element.io/
# 2. Створіть тестову кімнату
# 3. Скопіюйте room_id з URL кімнати
# 4. Оновіть username та password
