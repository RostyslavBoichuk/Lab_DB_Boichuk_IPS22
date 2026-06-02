"""
================================================================================
МОДЕЛІ БАЗИ ДАНИХ (Database Models - models.py)
================================================================================

ПРИЗНАЧЕННЯ:
Визначення структури бази даних через ORM (Object-Relational Mapping) 
SQLAlchemy. Кожен клас представляє таблицю в БД SQLite.

ФУНКЦІОНАЛ:
1. Визначення 8 основних моделей (сутностей):
   - Director (Директор)
   - Organization (Організація)
   - Laboratory (Лабораторія)
   - Expedition (Експедиція)
   - Role (Роль)
   - Researcher (Дослідник)
   - Equipment (Обладнання)
   - Contract (Контракт)

2. Визначення 4 асоціативних таблиць (M-to-M зв'язки):
   - expedition_researchers (Експедиції ↔ Дослідники)
   - finances (Організації ↔ Експедиції)
   - expedition_equipment (Експедиції ↔ Обладнання)
   - researcher_equipment (Дослідники ↔ Обладнання)

3. Визначення зв'язків між таблицями (relationships)

СТРУКТУРА МОДЕЛІ:
class TableName(db.Model):
    __tablename__ = 'table_name'  # Назва таблиці в БД
    
    # ПЕРВИННИЙ КЛЮЧ
    id = db.Column(db.Integer, primary_key=True)
    
    # ЗВИЧАЙНІ ПОЛЯ
    field_name = db.Column(db.String(255), nullable=False)
    
    # ІНОЗЕМНІ КЛЮЧІ (Foreign Keys)
    related_table_id = db.Column(db.Integer, db.ForeignKey('related_table.id'))
    
    # ЗВ'ЯЗКИ (Relationships)
    related_records = db.relationship('RelatedClass', backref='parent', lazy=True)

ТИПИ ПОЛІВ SQLAlchemy:
- db.Integer        → Integer (число без дробової частини)
- db.String(n)      → VARCHAR(n) (текст до n символів)
- db.Float          → Float (число з дробовою частиною)
- db.Date           → Date (дата у форматі YYYY-MM-DD)
- db.DateTime       → DateTime (дата та час)
- db.Boolean        → Boolean (True/False)
- db.Text           → Text (великий текст)

ОБМЕЖЕННЯ:
- primary_key=True  → Первинний ключ (унікальний, не null)
- nullable=False    → Поле обов'язкове (NOT NULL)
- nullable=True     → Поле опціональне (може бути NULL)
- unique=True       → Значення повинне бути унікальне
- default=value     → Значення за замовчуванням

ЗВ'ЯЗКИ (Relationships):
- db.relationship() визначає як таблиці пов'язані у Python (не створює FK)
- backref='name'    → Зворотна посилка на батьківський запис
- lazy=True/False   → Як завантажувати пов'язані записи

================================================================================
ЯК ДОДАТИ НОВУ МОДЕЛЬ:
================================================================================

1. Визначити структуру (поля, типи, обмеження):

class MyEntity(db.Model):
    \"\"\"Моя сутність - MyEntity\"\"\"
    __tablename__ = 'my_entities'
    
    # Первинний ключ
    id = db.Column(db.Integer, primary_key=True)
    
    # Звичайні поля
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    created_date = db.Column(db.Date, nullable=False)
    
    # Іноземний ключ
    parent_id = db.Column(db.Integer, db.ForeignKey('parent_table.id'), nullable=False)
    
    # Зв'язки
    children = db.relationship('ChildEntity', backref='parent', lazy=True)
    
    def __repr__(self):
        return f'<MyEntity {self.name}>'

2. Додати форму в forms.py (див. документацію forms.py)

3. Додати маршрути в app.py (див. документацію app.py)

4. Додати шаблони в templates/ (див. приклади)

5. Оновити БД (запустити seed_data.py або видалити expeditions.db для пересоздання)

================================================================================
ЯК ПРАЦЮЄ ЛОГІКА:
================================================================================

1. ВКЛАДЕННЯ КЛАСУ (Class Definition):
   class Director(db.Model):  → SQLAlchemy автоматично створює таблицю 'directors'

2. ПРИЗНАЧЕННЯ ПОЛІВ (Field Mapping):
   id = db.Column(db.Integer, primary_key=True)  → Стовпець 'id' типу INTEGER PRIMARY KEY
   full_name = db.Column(db.String(255), ...)   → Стовпець 'full_name' типу VARCHAR(255)

3. ПЕРВИННІ КЛЮЧІ (Primary Keys):
   id = db.Column(db.Integer, primary_key=True)  → Автоматично INCREMENT
   id = db.Column(db.String(50), primary_key=True)  → Рядковий PK (вручну назначається)

4. ІНОЗЕМНІ КЛЮЧІ (Foreign Keys):
   director_id = db.Column(db.Integer, db.ForeignKey('directors.id'))
   ↓
   organization.director_id посилається на director.id

5. ЗВ'ЯЗКИ (Relationships):
   organizations = db.relationship('Organization', backref='director', lazy=True)
   ↓
   director.organizations  → Список усіх організацій цього директора
   organization.director   → Директор цієї організації (зворотна посилка)

6. АСОЦІАТИВНІ ТАБЛИЦІ (Association Tables):
   expedition_researchers = db.Table(...)  → Таблиця без Python моделі
   expedition.researchers                  → Список дослідників експедиції
   researcher.expeditions                  → Список експедицій дослідника

7. SELF-REFERENCE (Самовідсилка):
   supervisor_id = db.Column(db.String(50), db.ForeignKey('researchers.id'))
   ↓
   researcher.supervisor      → Керівник цього дослідника
   researcher.supervised      → Список дослідників, яких веде цей дослідник

================================================================================
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ============================================================================
# ОСНОВНІ ТАБЛИЦІ (Main Entities)
# ============================================================================

class Director(db.Model):
    """ДИРЕКТОР - Director/Manager"""
    __tablename__ = 'directors'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)  # ПІБ
    appointment_date = db.Column(db.Date, nullable=False)  # Дата призначення
    
    # Relationships
    organizations = db.relationship('Organization', backref='director', lazy=True)
    expeditions = db.relationship('Expedition', backref='director', lazy=True)
    
    def __repr__(self):
        return f'<Director {self.full_name}>'


class Organization(db.Model):
    """ОРГАНІЗАЦІЯ - Organization"""
    __tablename__ = 'organizations'
    
    id = db.Column(db.String(50), primary_key=True)  # Ідентифікатор
    name = db.Column(db.String(255), nullable=False)  # Назва
    country = db.Column(db.String(100), nullable=False)  # Країна
    year_founded = db.Column(db.Integer, nullable=False)  # Рік заснування
    director_id = db.Column(db.Integer, db.ForeignKey('directors.id'), nullable=False)
    
    # Relationships
    laboratories = db.relationship('Laboratory', backref='organization', lazy=True)
    contracts = db.relationship('Contract', backref='organization', lazy=True)
    
    def __repr__(self):
        return f'<Organization {self.name}>'


class Laboratory(db.Model):
    """ЛАБОРАТОРІЯ - Laboratory"""
    __tablename__ = 'laboratories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)  # Назва
    num_employees = db.Column(db.Integer, nullable=False)  # Кількість співробітників
    activities = db.Column(db.String(500))  # Напрями діяльності
    organization_id = db.Column(db.String(50), db.ForeignKey('organizations.id'), nullable=False)
    
    # Relationships
    researchers = db.relationship('Researcher', backref='laboratory', lazy=True)
    equipment = db.relationship('Equipment', backref='laboratory', lazy=True)
    
    def __repr__(self):
        return f'<Laboratory {self.name}>'


class Expedition(db.Model):
    """ЕКСПЕДИЦІЯ - Expedition"""
    __tablename__ = 'expeditions'
    
    id = db.Column(db.String(50), primary_key=True)  # Індекс
    name = db.Column(db.String(255), nullable=False)  # Назва
    start_date = db.Column(db.Date, nullable=False)  # Дата початку
    end_date = db.Column(db.Date, nullable=False)  # Дата закінчення
    region = db.Column(db.String(100), nullable=False)  # Регіон
    director_id = db.Column(db.Integer, db.ForeignKey('directors.id'), nullable=False)
    
    # Relationships
    researchers = db.relationship('Researcher', secondary='expedition_researchers', backref='expeditions')
    organizations = db.relationship('Organization', secondary='finances', backref='expeditions')
    equipment = db.relationship('Equipment', secondary='expedition_equipment', backref='expeditions')
    
    def __repr__(self):
        return f'<Expedition {self.name}>'


class Role(db.Model):
    """РОЛЬ - Role"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Назва ролі
    description = db.Column(db.String(255))  # Опис
    
    # Relationships
    researchers = db.relationship('Researcher', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'


class Researcher(db.Model):
    """ДОСЛІДНИК - Researcher"""
    __tablename__ = 'researchers'
    
    id = db.Column(db.String(50), primary_key=True)  # ПІБ або ID
    full_name = db.Column(db.String(255), nullable=False)  # ПІБ
    specialization = db.Column(db.String(255))  # Спеціалізація
    hire_date = db.Column(db.Date, nullable=False)  # Дата прийняття
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    laboratory_id = db.Column(db.Integer, db.ForeignKey('laboratories.id'), nullable=False)
    supervisor_id = db.Column(db.String(50), db.ForeignKey('researchers.id'), nullable=True)
    
    # Relationships
    contracts = db.relationship('Contract', backref='researcher', lazy=True)
    supervised = db.relationship('Researcher', foreign_keys=[supervisor_id], remote_side=[id], backref='supervisor')
    equipment = db.relationship('Equipment', secondary='researcher_equipment', backref='researchers')
    
    def __repr__(self):
        return f'<Researcher {self.full_name}>'


class Equipment(db.Model):
    """ОБЛАДНАННЯ - Equipment"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)  # Назва
    equipment_type = db.Column(db.String(100), nullable=False)  # Тип обладнання
    cost = db.Column(db.Float, nullable=False)  # Вартість
    purchase_date = db.Column(db.Date, nullable=False)  # Дата придбання
    laboratory_id = db.Column(db.Integer, db.ForeignKey('laboratories.id'), nullable=False)
    
    def __repr__(self):
        return f'<Equipment {self.name}>'


class Contract(db.Model):
    """КОНТРАКТ - Contract"""
    __tablename__ = 'contracts'
    
    id = db.Column(db.String(50), primary_key=True)  # Індекс контракту
    title = db.Column(db.String(255), nullable=False)  # Назва
    start_date = db.Column(db.Date, nullable=False)  # Дата початку
    end_date = db.Column(db.Date, nullable=False)  # Дата закінчення
    budget = db.Column(db.Float, nullable=False)  # Бюджет
    researcher_id = db.Column(db.String(50), db.ForeignKey('researchers.id'), nullable=False)
    organization_id = db.Column(db.String(50), db.ForeignKey('organizations.id'), nullable=False)
    
    def __repr__(self):
        return f'<Contract {self.title}>'


# ============================================================================
# АСОЦІАТИВНІ ТАБЛИЦІ (Association Tables)
# ============================================================================

expedition_researchers = db.Table(
    'expedition_researchers',
    db.Column('expedition_id', db.String(50), db.ForeignKey('expeditions.id'), primary_key=True),
    db.Column('researcher_id', db.String(50), db.ForeignKey('researchers.id'), primary_key=True)
)

finances = db.Table(
    'finances',
    db.Column('organization_id', db.String(50), db.ForeignKey('organizations.id'), primary_key=True),
    db.Column('expedition_id', db.String(50), db.ForeignKey('expeditions.id'), primary_key=True)
)

expedition_equipment = db.Table(
    'expedition_equipment',
    db.Column('expedition_id', db.String(50), db.ForeignKey('expeditions.id'), primary_key=True),
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
)

researcher_equipment = db.Table(
    'researcher_equipment',
    db.Column('researcher_id', db.String(50), db.ForeignKey('researchers.id'), primary_key=True),
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
)
