"""
================================================================================
КОНФІГУРАЦІЯ ДОДАТКА (Configuration - config.py)
================================================================================

ПРИЗНАЧЕННЯ:
Налаштування Flask додатка та бази даних. Визначає шляхи до БД, 
секретні ключі, та інші параметри.

ФУНКЦІОНАЛ:
1. Налаштування SQLAlchemy та SQLite БД
2. Налаштування Flask Сесій
3. Налаштування CSRF захисту
4. Можливість змінити на іншу БД (MySQL, PostgreSQL, MSSQL)

ВАЖЛИВІ ПАРАМЕТРИ:
- SQLALCHEMY_DATABASE_URI     → Шлях до БД файлу або URL БД сервера
- SQLALCHEMY_TRACK_MODIFICATIONS → Вимкнути попередження про модифікації
- SECRET_KEY                  → Секретний ключ для CSRF та Sessions
- PERMANENT_SESSION_LIFETIME  → Тривалість сесії користувача

================================================================================
ЯК ЗМІНИТИ НАЗВУ/ШЛЯХ БД:
================================================================================

1. Поточна конфігурація (SQLite локальний файл):
   
   SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir}/expeditions.db'
   
   → Створює файл expeditions.db в папці проекту

2. Змінити шлях БД:
   
   SQLALCHEMY_DATABASE_URI = 'sqlite:////path/to/my_database.db'
   
   → Абсолютний шлях до файлу БД

3. MySQL (сервер в мережі):
   
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/dbname'
   
   Встановити драйвер: pip install pymysql

4. PostgreSQL:
   
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/dbname'
   
   Встановити драйвер: pip install psycopg2

5. Microsoft SQL Server:
   
   SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://user:password@servername/dbname?driver=ODBC+Driver+17+for+SQL+Server'
   
   Встановити драйвер: pip install pyodbc

6. MS Access (альтернатива SQLite):
   
   SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc:///?odbc_connect=...'
   
   Див. коментар у файлі

================================================================================
ЯК ЗМІНИТИ СЕКРЕТНИЙ КЛЮЧ:
================================================================================

1. Поточний SECRET_KEY (тільки для розроблення):
   
   SECRET_KEY = 'dev-secret-key-change-in-production'
   
   ⚠️ НЕБЕЗПЕЧНО для production!

2. Генерувати новий безпечний ключ:
   
   import os
   SECRET_KEY = os.urandom(24).hex()
   
   або
   
   import secrets
   SECRET_KEY = secrets.token_hex(32)

3. Використовувати змінну оточення:
   
   SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key')
   
   Задати в системі:
   set SECRET_KEY=my-super-secret-key  (Windows)
   export SECRET_KEY=my-super-secret-key  (Linux/Mac)

================================================================================
ЯК НАЛАШТУВАТИ СЕСІЇ:
================================================================================

1. Поточна конфігурація (1 день):
   
   PERMANENT_SESSION_LIFETIME = timedelta(days=1)
   
   Користувач залишається в системі 1 день

2. Інші приклади:
   
   timedelta(hours=2)      → 2 години
   timedelta(minutes=30)   → 30 хвилин
   timedelta(days=7)       → 7 днів
   timedelta(weeks=1)      → 1 тиждень

3. Безпечні cookies (HTTPS тільки):
   
   SESSION_COOKIE_SECURE = True
   SESSION_COOKIE_HTTPONLY = True
   SESSION_COOKIE_SAMESITE = 'Lax'

================================================================================
"""
import os
from datetime import timedelta

class Config:
    """Database configuration"""
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite database (you can change to MySQL, PostgreSQL, or MSSQL)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir}/expeditions.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # For MS Access database (alternative):
    # SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc:///?odbc_connect=Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=Реалізація Бойчук.accdb;'
    
    SECRET_KEY = 'dev-secret-key-change-in-production'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
