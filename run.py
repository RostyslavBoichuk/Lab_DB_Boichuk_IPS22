#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ТОЧКА ВХОДУ ДОДАТКА (Application Entry Point - run.py)
================================================================================

ПРИЗНАЧЕННЯ:
Скрипт для запуску Flask веб-сервера. Це основний файл, який запускається 
при старті додатка.

ФУНКЦІОНАЛ:
1. Ініціалізація Flask додатка (app)
2. Ініціалізація бази даних (db)
3. Запуск розробницького веб-сервера
4. Активація режиму DEBUG для перезавантаження при змінах файлів

ЗАПУСК:
python run.py
↓
Сервер запускається на http://localhost:5000

================================================================================
ЯК ЗАПУСТИТИ ДОДАТОК:
================================================================================

1. Встановити залежності:
   pip install -r requirements.txt

2. Запустити додаток:
   python run.py

3. Відкрити у браузері:
   http://localhost:5000

4. Зупинити сервер:
   Ctrl+C (у терміналі)

================================================================================
ЯК ЗМІНИТИ ПОРТ СЕРВЕРА:
================================================================================

Поточна конфігурація (з файлу):
app.run(debug=True, host='localhost', port=5000)

1. Змінити порт на 8000:
   app.run(debug=True, host='localhost', port=8000)
   → http://localhost:8000

2. Дозволити доступ з інших машин:
   app.run(debug=True, host='0.0.0.0', port=5000)
   → Доступна для інших комп'ютерів у мережі

3. Вимкнути DEBUG режим (для production):
   app.run(debug=False, host='0.0.0.0', port=80)
   → Повільне перезавантаження, повнофункціональний

================================================================================
ЯК ПРАЦЮЄ ЛОГІКА:
================================================================================

1. ІМПОРТ:
   from app import app, db
   → Завантажуються Flask додаток та база даних

2. СТВОРЕННЯ ДОДАТКА:
   app.run()
   → Flask створює веб-сервер

3. ЗАПУСК СЕРВЕРА:
   http://localhost:5000
   → Браузер подає запит на сервер

4. ОБРОБКА ЗАПИТУ:
   Flask маршрутизує запит на відповідний route (app.py)
   → Обробка логіки (CRUD, запити, звіти)
   → Взаємодія з БД (models.py, queries.py)

5. ВІДПОВІДЬ:
   Flask повертає HTML сторінку у браузер

6. DISPLAY:
   Браузер показує сторінку користувачу

================================================================================
ЗМІННІ ОТОЧЕННЯ:
================================================================================

1. Встановити режим розробки (Windows):
   set FLASK_ENV=development
   set FLASK_APP=run.py
   flask run

2. Встановити режим production (Linux/Mac):
   export FLASK_ENV=production
   export FLASK_APP=run.py
   flask run

3. Встановити SECRET_KEY (для безпеки):
   set SECRET_KEY=my-secret-key
   python run.py

================================================================================
Database Management System - Expedition Management Interface
Python Flask Web Application for Lab Work #2

This application provides a complete web-based database management system for 
research expeditions with support for organizations, laboratories, researchers,
contracts, and more.
"""

import sys
import os

# Ensure the current directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (Director, Organization, Laboratory, Expedition, Role, 
                    Researcher, Equipment, Contract)

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'Director': Director,
        'Organization': Organization,
        'Laboratory': Laboratory,
        'Expedition': Expedition,
        'Role': Role,
        'Researcher': Researcher,
        'Equipment': Equipment,
        'Contract': Contract
    }

if __name__ == '__main__':
    print("Starting Expedition Management System...")
    print("Visit: http://localhost:5000/")
    app.run(debug=True, host='localhost', port=5000)
