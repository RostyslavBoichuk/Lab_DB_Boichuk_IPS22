"""
================================================================================
СКРИПТ ЗАПОВНЕННЯ БД ТЕСТОВИМИ ДАНИМИ (Seed Database - seed_data.py)
================================================================================

ПРИЗНАЧЕННЯ:
Скрипт автоматично заповнює базу даних тестовими даними для демонстрації 
та тестування функціональності додатка.

ФУНКЦІОНАЛ:
1. Видалення старих даних (db.drop_all())
2. Створення нових таблиць (db.create_all())
3. Додавання тестових записів для всіх 8 сутностей
4. Налаштування M-to-M зв'язків через асоціативні таблиці

ТЕСТОВІ ДАНІ:
- 4 директори
- 4 організації
- 6 лабораторій
- 5 ролей
- 10+ дослідників (з self-reference для керівників)
- 8+ одиниць обладнання
- 8 контрактів
- 8 експедицій
- М-to-М зв'язки (участь дослідників, обладнання, фінансування)

ЗАПУСК:
python seed_data.py
↓
База даних заповнюється тестовими даними
Готово до використання!

================================================================================
ЯК ЗАПУСТИТИ SEED СКРИПТ:
================================================================================

1. Стандартна команда:
   python seed_data.py

2. Забезпечити, що залежності встановлені:
   pip install -r requirements.txt
   python seed_data.py

3. Для перезаповнення БД (видалити старі дані):
   python seed_data.py
   (автоматично видаляє db.drop_all())

4. Перевірити результат:
   python run.py
   → Відкрити http://localhost:5000
   → Переглянути дані у системі

================================================================================
СТРУКТУРА SEED СКРИПТУ:
================================================================================

1. ДИРЕКТОРИ (Directors):
   - Петренко Іван - 2015
   - Коваль Марія - 2016
   - Шевченко Олег - 2014
   - Павлова Ольга - 2017

2. ОРГАНІЗАЦІЇ (Organizations):
   - ORG001 - НАНУ (Україна, 1918) → Директор: Петренко
   - ORG002 - КНУ (Україна, 1834) → Директор: Коваль
   - ORG003 - Міжнародний центр (Франція, 1995) → Директор: Шевченко
   - ORG004 - Європейський інститут (Швейцарія, 2005) → Директор: Павлова

3. ЛАБОРАТОРІЇ (Laboratories):
   - НАНУ → Лабораторія інформатики (15 осіб)
   - НАНУ → Лабораторія фізики (12 осіб)
   - КНУ → Лабораторія хімії (10 осіб)
   - ... і так далі

4. РОЛІ (Roles):
   - Старший науковий співробітник
   - Науковий співробітник
   - Молодший науковий співробітник
   - Асистент
   - Інженер

5. ДОСЛІДНИКИ (Researchers):
   - RES001 - Петренко Іван (Лаб. інформатики, Роль: Старший)
   - RES002 - Коваль Марія (Лаб. фізики, Роль: Науковий)
   - RES003 - Сідоров Петро (Лаб. хімії, Роль: Молодший) → Керівник: Петренко
   - ... і так далі

6. ОБЛАДНАННЯ (Equipment):
   - Сервер (Лаб. інформатики) - 80000
   - Персональний комп'ютер (Лаб. фізики) - 45000
   - Мікроскоп (Лаб. хімії) - 65000
   - ... і так далі

7. КОНТРАКТИ (Contracts):
   - CNT001 - Розробка ПЗ (Петренко Іван, НАНУ) - 150000
   - CNT002 - Аналіз даних (Коваль Марія, КНУ) - 100000
   - ... і так далі

8. ЕКСПЕДИЦІЇ (Expeditions):
   - EXP001 - Тропічні дослідження (Африка, 2021-2023)
   - EXP002 - Дослідження мегафауни (Азія, 2022-2023)
   - ... і так далі

9. М-to-М ЗВ'ЯЗКИ:
   - expedition_researchers: які дослідники беруть участь в експедиціях
   - finances: які організації фінансують експедиції
   - expedition_equipment: яке обладнання використовується в експедиціях
   - researcher_equipment: яким обладнанням користуються дослідники

================================================================================
ЯК ДОДАТИ БІЛЬШЕ ТЕСТОВИХ ДАНИХ:
================================================================================

1. Додати нового директора:

directors.append(
    Director(
        full_name='Назва ПІБ',
        appointment_date=date(2020, 1, 15)
    )
)
db.session.add(directors[-1])

2. Додати нову організацію:

organizations.append(
    Organization(
        id='ORG099',
        name='Назва організації',
        country='Країна',
        year_founded=2020,
        director_id=directors[0].id  # Посилання на директора
    )
)
db.session.add(organizations[-1])

3. Додати М-to-М зв'язок (дослідник в експедиції):

expedition_researchers.insert().values(
    expedition_id='EXP001',
    researcher_id='RES001'
)

4. На кінець скрипту ЗАВЖДИ викликати:

db.session.commit()
print("✅ Database seeded successfully!")

================================================================================
ВАЖЛИВО:
================================================================================

Всі первинні ключі автоматично генеруються:
- Director.id → AUTO_INCREMENT
- Laboratory.id → AUTO_INCREMENT
- Role.id → AUTO_INCREMENT
- Equipment.id → AUTO_INCREMENT

Строкові первинні ключі мають бути унікальні:
- Organization.id = 'ORG001' → Унікальна
- Expedition.id = 'EXP001' → Унікальна
- Researcher.id = 'RES001' → Унікальна
- Contract.id = 'CNT001' → Унікальна

Іноземні ключи повинні посилатися на існуючі записи:
- Organization.director_id → ПОВИННА існувати Director з цим id
- Laboratory.organization_id → ПОВИННА існувати Organization з цим id
- Expedition.director_id → ПОВИННА існувати Director з цим id

================================================================================
"""

from app import app, db
from models import Director, Organization, Laboratory, Expedition, Role, Researcher, Equipment, Contract, expedition_researchers, finances, expedition_equipment, researcher_equipment
from datetime import datetime, date

def seed_database():
    """Populate database with test data"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("Seeding database with test data...")
        
        # =====================================================================

        # CREATE DIRECTORS (Директори)
        # =====================================================================
        print("Creating Directors...")
        directors = [
            Director(full_name='Петренко Іван Миколайович', 
                    appointment_date=date(2015, 1, 15)),
            Director(full_name='Коваль Марія Сергіївна', 
                    appointment_date=date(2016, 3, 20)),
            Director(full_name='Шевченко Олег Петрович', 
                    appointment_date=date(2014, 6, 10)),
            Director(full_name='Павлова Ольга Іванівна', 
                    appointment_date=date(2017, 9, 1)),
        ]
        db.session.add_all(directors)
        db.session.flush()  # Get IDs without committing
        
        # =====================================================================
        # CREATE ORGANIZATIONS (Організації)
        # =====================================================================
        print("Creating Organizations...")
        organizations = [
            Organization(id='ORG001', name='Національна академія наук України',
                        country='Україна', year_founded=1918, director_id=directors[0].id),
            Organization(id='ORG002', name='Міжнародний центр науки',
                        country='Франція', year_founded=1995, director_id=directors[1].id),
            Organization(id='ORG003', name='Європейський дослідницький центр',
                        country='Німеччина', year_founded=1990, director_id=directors[2].id),
            Organization(id='ORG004', name='Науково-технічний комплекс',
                        country='Україна', year_founded=2005, director_id=directors[3].id),
        ]
        db.session.add_all(organizations)
        db.session.flush()
        
        # =====================================================================
        # CREATE LABORATORIES (Лабораторії)
        # =====================================================================
        print("Creating Laboratories...")
        laboratories = [
            Laboratory(name='Лабораторія інформатики',
                      num_employees=15, activities='Розробка програмного забезпечення',
                      organization_id='ORG001'),
            Laboratory(name='Лабораторія фізики',
                      num_employees=12, activities='Дослідження квантових явищ',
                      organization_id='ORG001'),
            Laboratory(name='Лабораторія хімії',
                      num_employees=10, activities='Органічна та неорганічна хімія',
                      organization_id='ORG002'),
            Laboratory(name='Лабораторія біології',
                      num_employees=18, activities='Молекулярна біологія',
                      organization_id='ORG002'),
            Laboratory(name='Лабораторія матеріалознавства',
                      num_employees=14, activities='Нові матеріали',
                      organization_id='ORG003'),
            Laboratory(name='Лабораторія екології',
                      num_employees=8, activities='Екологічний моніторинг',
                      organization_id='ORG004'),
        ]
        db.session.add_all(laboratories)
        db.session.flush()
        
        # =====================================================================
        # CREATE ROLES (Ролі)
        # =====================================================================
        print("Creating Roles...")
        roles = [
            Role(name='Старший науковий співробітник', description='Вищий рівень науковців'),
            Role(name='Науковий співробітник', description='Постійні працівники'),
            Role(name='Молодший науковий співробітник', description='Початкуючі дослідники'),
            Role(name='Асистент', description='Допоміжний персонал'),
            Role(name='Інженер', description='Технічні спеціалісти'),
        ]
        db.session.add_all(roles)
        db.session.flush()
        
        # =====================================================================
        # CREATE RESEARCHERS (Дослідники)
        # =====================================================================
        print("Creating Researchers...")
        researchers = [
            # Лабораторія інформатики (ORG001)
            Researcher(id='RES001', full_name='Бойчук Максим Вікторович',
                      specialization='Програмування', hire_date=date(2015, 1, 1),
                      role_id=roles[0].id, laboratory_id=laboratories[0].id),
            Researcher(id='RES002', full_name='Сидоренко Євген Ростиславович',
                      specialization='Кібербезпека', hire_date=date(2016, 3, 15),
                      role_id=roles[1].id, laboratory_id=laboratories[0].id),
            Researcher(id='RES003', full_name='Грінь Аліса Юріївна',
                      specialization='Штучний інтелект', hire_date=date(2018, 9, 1),
                      role_id=roles[2].id, laboratory_id=laboratories[0].id, supervisor_id='RES001'),
            
            # Лабораторія фізики (ORG001)
            Researcher(id='RES004', full_name='Романський Борис Ігоревич',
                      specialization='Квантова механіка', hire_date=date(2014, 6, 1),
                      role_id=roles[0].id, laboratory_id=laboratories[1].id),
            Researcher(id='RES005', full_name='Федоренко Юлія Миколаївна',
                      specialization='Фізика твердого тіла', hire_date=date(2017, 1, 15),
                      role_id=roles[1].id, laboratory_id=laboratories[1].id),
            
            # Лабораторія хімії (ORG002)
            Researcher(id='RES006', full_name='Маркевич Василь Станіславович',
                      specialization='Органічна синтез', hire_date=date(2013, 9, 1),
                      role_id=roles[0].id, laboratory_id=laboratories[2].id),
            Researcher(id='RES007', full_name='Цимбал Тетяна Павлівна',
                      specialization='Аналітична хімія', hire_date=date(2019, 2, 15),
                      role_id=roles[2].id, laboratory_id=laboratories[2].id, supervisor_id='RES006'),
            
            # Лабораторія біології (ORG002)
            Researcher(id='RES008', full_name='Козаков Вадим Геннадійович',
                      specialization='Молекулярна біологія', hire_date=date(2012, 5, 1),
                      role_id=roles[0].id, laboratory_id=laboratories[3].id),
            Researcher(id='RES009', full_name='Левинська Ірина Сергіївна',
                      specialization='Генетика', hire_date=date(2016, 8, 1),
                      role_id=roles[1].id, laboratory_id=laboratories[3].id),
            Researcher(id='RES010', full_name='Морозов Сергій Олегович',
                      specialization='Біотехнологія', hire_date=date(2018, 1, 15),
                      role_id=roles[2].id, laboratory_id=laboratories[3].id, supervisor_id='RES008'),
            
            # Лабораторія матеріалознавства (ORG003)
            Researcher(id='RES011', full_name='Фурс Дмитро Леонідович',
                      specialization='Полімерні матеріали', hire_date=date(2014, 3, 1),
                      role_id=roles[0].id, laboratory_id=laboratories[4].id),
            Researcher(id='RES012', full_name='Вовк Анна Олександрівна',
                      specialization='Композитні матеріали', hire_date=date(2017, 6, 15),
                      role_id=roles[1].id, laboratory_id=laboratories[4].id),
            
            # Лабораторія екології (ORG004)
            Researcher(id='RES013', full_name='Кравець Петро Миколайович',
                      specialization='Екотоксикологія', hire_date=date(2011, 1, 1),
                      role_id=roles[0].id, laboratory_id=laboratories[5].id),
            Researcher(id='RES014', full_name='Романова Людмила Вікторівна',
                      specialization='Водна екологія', hire_date=date(2015, 9, 1),
                      role_id=roles[1].id, laboratory_id=laboratories[5].id),
            
            # Додаткові дослідники з тією ж спеціалізацією в одній лабораторії
            # Для запиту 8 (Колеги в одній лабораторії)
            Researcher(id='RES015', full_name='Петренко Ганна Іванівна',
                      specialization='Програмування', hire_date=date(2016, 6, 1),
                      role_id=roles[2].id, laboratory_id=laboratories[0].id, supervisor_id='RES001'),
            Researcher(id='RES016', full_name='Козак Максим Анатолійович',
                      specialization='Молекулярна біологія', hire_date=date(2019, 3, 1),
                      role_id=roles[2].id, laboratory_id=laboratories[3].id, supervisor_id='RES008'),
        ]
        db.session.add_all(researchers)
        db.session.flush()
        
        # =====================================================================
        # CREATE EXPEDITIONS (Експедиції)
        # =====================================================================
        print("Creating Expeditions...")
        expeditions = [
            Expedition(id='EXP001', name='Українські Карпати 2022',
                      start_date=date(2022, 6, 1), end_date=date(2022, 8, 31),
                      region='Карпати', director_id=directors[0].id),
            Expedition(id='EXP002', name='Азовське море 2023',
                      start_date=date(2023, 5, 15), end_date=date(2023, 9, 15),
                      region='Азовське море', director_id=directors[1].id),
            Expedition(id='EXP003', name='Альпи 2023',
                      start_date=date(2023, 7, 1), end_date=date(2023, 8, 31),
                      region='Альпи', director_id=directors[2].id),
            Expedition(id='EXP004', name='Кавказ 2024',
                      start_date=date(2024, 6, 1), end_date=date(2024, 8, 31),
                      region='Кавказ', director_id=directors[3].id),
        ]
        db.session.add_all(expeditions)
        db.session.flush()
        
        # =====================================================================
        # ASSIGN RESEARCHERS TO EXPEDITIONS (Many-to-Many)
        # =====================================================================
        print("Assigning researchers to expeditions...")
        # EXP001 - Карпати
        expeditions[0].researchers.extend([researchers[0], researchers[1], researchers[2], researchers[5], researchers[6]])
        
        # EXP002 - Азовське море
        expeditions[1].researchers.extend([researchers[0], researchers[3], researchers[8], researchers[9], researchers[10]])
        
        # EXP003 - Альпи
        expeditions[2].researchers.extend([researchers[0], researchers[3], researchers[5], researchers[11], researchers[12]])
        
        # EXP004 - Кавказ
        expeditions[3].researchers.extend([researchers[0], researchers[1], researchers[4], researchers[9], researchers[13]])
        
        # Ensure RES001 (Бойчук) is in all expeditions for Query 7
        if researchers[0] not in expeditions[0].researchers:
            expeditions[0].researchers.append(researchers[0])
        if researchers[0] not in expeditions[1].researchers:
            expeditions[1].researchers.append(researchers[0])
        if researchers[0] not in expeditions[2].researchers:
            expeditions[2].researchers.append(researchers[0])
        if researchers[0] not in expeditions[3].researchers:
            expeditions[3].researchers.append(researchers[0])
        
        # =====================================================================
        # CREATE EQUIPMENT (Обладнання)
        # =====================================================================
        print("Creating Equipment...")
        equipment = [
            Equipment(name='Лазерний спектрометр', equipment_type='Спектрометр',
                     cost=45000.00, purchase_date=date(2018, 3, 15),
                     laboratory_id=laboratories[0].id),
            Equipment(name='Електронний мікроскоп', equipment_type='Мікроскоп',
                     cost=125000.00, purchase_date=date(2017, 6, 1),
                     laboratory_id=laboratories[1].id),
            Equipment(name='ЯМР спектрометр', equipment_type='Спектрометр',
                     cost=350000.00, purchase_date=date(2019, 1, 10),
                     laboratory_id=laboratories[2].id),
            Equipment(name='Проточний цитометр', equipment_type='Аналізатор',
                     cost=180000.00, purchase_date=date(2020, 5, 20),
                     laboratory_id=laboratories[3].id),
            Equipment(name='Термічний аналізатор', equipment_type='Аналізатор',
                     cost=75000.00, purchase_date=date(2019, 9, 15),
                     laboratory_id=laboratories[4].id),
            Equipment(name='Газовий хроматограф', equipment_type='Хроматограф',
                     cost=55000.00, purchase_date=date(2021, 2, 1),
                     laboratory_id=laboratories[5].id),
            Equipment(name='Магнітний резонанс', equipment_type='ЯМР',
                     cost=250000.00, purchase_date=date(2016, 11, 15),
                     laboratory_id=laboratories[0].id),
            Equipment(name='Конфокальний мікроскоп', equipment_type='Мікроскоп',
                     cost=200000.00, purchase_date=date(2018, 8, 10),
                     laboratory_id=laboratories[3].id),
        ]
        db.session.add_all(equipment)
        db.session.flush()
        
        # =====================================================================
        # CREATE CONTRACTS (Контракти)
        # =====================================================================
        print("Creating Contracts...")
        contracts = [
            Contract(id='CNT001', title='Дослідження штучного інтелекту',
                    start_date=date(2022, 1, 1), end_date=date(2024, 12, 31),
                    budget=500000.00, researcher_id='RES001', organization_id='ORG001'),
            Contract(id='CNT002', title='Розробка кібербезпеки',
                    start_date=date(2023, 6, 1), end_date=date(2025, 5, 31),
                    budget=350000.00, researcher_id='RES002', organization_id='ORG001'),
            Contract(id='CNT003', title='Квантові обчислення',
                    start_date=date(2021, 1, 1), end_date=date(2024, 12, 31),
                    budget=750000.00, researcher_id='RES004', organization_id='ORG002'),
            Contract(id='CNT004', title='Органічний синтез',
                    start_date=date(2022, 3, 15), end_date=date(2024, 3, 14),
                    budget=200000.00, researcher_id='RES006', organization_id='ORG002'),
            Contract(id='CNT005', title='Молекулярна біологія',
                    start_date=date(2023, 1, 1), end_date=date(2025, 12, 31),
                    budget=600000.00, researcher_id='RES008', organization_id='ORG002'),
            Contract(id='CNT006', title='Матеріали майбутнього',
                    start_date=date(2022, 9, 1), end_date=date(2025, 8, 31),
                    budget=800000.00, researcher_id='RES011', organization_id='ORG003'),
            Contract(id='CNT007', title='Екологічний моніторинг',
                    start_date=date(2023, 4, 1), end_date=date(2024, 3, 31),
                    budget=250000.00, researcher_id='RES013', organization_id='ORG004'),
            Contract(id='CNT008', title='Інноваційні методи',
                    start_date=date(2024, 1, 1), end_date=date(2026, 12, 31),
                    budget=450000.00, researcher_id='RES009', organization_id='ORG002'),
        ]
        db.session.add_all(contracts)
        db.session.flush()
        
        # =====================================================================
        # ASSIGN ORGANIZATIONS TO EXPEDITIONS (Many-to-Many - ФІНАНСУЄ)
        # =====================================================================
        print("Assigning organizations to expeditions (finances)...")
        # EXP001 - Карпати
        db.session.execute(finances.insert().values([
            {'organization_id': 'ORG001', 'expedition_id': 'EXP001'},
            {'organization_id': 'ORG002', 'expedition_id': 'EXP001'},
        ]))
        
        # EXP002 - Азовське море
        db.session.execute(finances.insert().values([
            {'organization_id': 'ORG001', 'expedition_id': 'EXP002'},
            {'organization_id': 'ORG004', 'expedition_id': 'EXP002'},
        ]))
        
        # EXP003 - Альпи
        db.session.execute(finances.insert().values([
            {'organization_id': 'ORG002', 'expedition_id': 'EXP003'},
            {'organization_id': 'ORG003', 'expedition_id': 'EXP003'},
        ]))
        
        # EXP004 - Кавказ
        db.session.execute(finances.insert().values([
            {'organization_id': 'ORG003', 'expedition_id': 'EXP004'},
            {'organization_id': 'ORG004', 'expedition_id': 'EXP004'},
        ]))
        
        # =====================================================================
        # ASSIGN EQUIPMENT TO EXPEDITIONS (Many-to-Many - СКЛАДАЄТЬСЯ)
        # =====================================================================
        print("Assigning equipment to expeditions...")
        # EXP001 - Карпати
        db.session.execute(expedition_equipment.insert().values([
            {'expedition_id': 'EXP001', 'equipment_id': equipment[0].id},
            {'expedition_id': 'EXP001', 'equipment_id': equipment[1].id},
        ]))
        
        # EXP002 - Азовське море
        db.session.execute(expedition_equipment.insert().values([
            {'expedition_id': 'EXP002', 'equipment_id': equipment[2].id},
            {'expedition_id': 'EXP002', 'equipment_id': equipment[5].id},
        ]))
        
        # EXP003 - Альпи
        db.session.execute(expedition_equipment.insert().values([
            {'expedition_id': 'EXP003', 'equipment_id': equipment[1].id},
            {'expedition_id': 'EXP003', 'equipment_id': equipment[6].id},
        ]))
        
        # EXP004 - Кавказ
        db.session.execute(expedition_equipment.insert().values([
            {'expedition_id': 'EXP004', 'equipment_id': equipment[4].id},
            {'expedition_id': 'EXP004', 'equipment_id': equipment[7].id},
        ]))
        
        # =====================================================================
        # ASSIGN EQUIPMENT TO RESEARCHERS (Many-to-Many - ВИКОРИСТОВУЄ)
        # =====================================================================
        print("Assigning equipment to researchers...")
        # RES001 uses multiple equipment
        db.session.execute(researcher_equipment.insert().values([
            {'researcher_id': 'RES001', 'equipment_id': equipment[0].id},
            {'researcher_id': 'RES001', 'equipment_id': equipment[6].id},
        ]))
        
        # RES002
        db.session.execute(researcher_equipment.insert().values([
            {'researcher_id': 'RES002', 'equipment_id': equipment[0].id},
        ]))
        
        # RES004
        db.session.execute(researcher_equipment.insert().values([
            {'researcher_id': 'RES004', 'equipment_id': equipment[1].id},
            {'researcher_id': 'RES004', 'equipment_id': equipment[6].id},
        ]))
        
        # RES006
        db.session.execute(researcher_equipment.insert().values([
            {'researcher_id': 'RES006', 'equipment_id': equipment[2].id},
        ]))
        
        # RES008
        db.session.execute(researcher_equipment.insert().values([
            {'researcher_id': 'RES008', 'equipment_id': equipment[3].id},
            {'researcher_id': 'RES008', 'equipment_id': equipment[7].id},
        ]))
        
        # RES011
        db.session.execute(researcher_equipment.insert().values([
            {'researcher_id': 'RES011', 'equipment_id': equipment[4].id},
        ]))
        
        # RES013
        db.session.execute(researcher_equipment.insert().values([
            {'researcher_id': 'RES013', 'equipment_id': equipment[5].id},
        ]))
        
        # =====================================================================
        # COMMIT ALL DATA
        # =====================================================================
        db.session.commit()
        print("Database seeded successfully with test data!")
        print(f"   • {len(directors)} Directors")
        print(f"   • {len(organizations)} Organizations")
        print(f"   • {len(laboratories)} Laboratories")
        print(f"   • {len(roles)} Roles")
        print(f"   • {len(researchers)} Researchers")
        print(f"   • {len(expeditions)} Expeditions")
        print(f"   • {len(equipment)} Equipment items")
        print(f"   • {len(contracts)} Contracts")
        print(f"   • M-to-M relationships (ФІНАНСУЄ, СКЛАДАЄТЬСЯ, ВИКОРИСТОВУЄ) created")

if __name__ == '__main__':
    seed_database()
