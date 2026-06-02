"""
================================================================================
ЗАПИТИ ТА ЗВІТИ (Queries and Reports - queries.py)
================================================================================

ПРИЗНАЧЕННЯ:
Модуль містить всі параметризовані SQL запити та аналітичні звіти, 
реалізовані через SQLAlchemy ORM.

ФУНКЦІОНАЛ:
1. **8 параметризованих запитів** різної складності:
   - Запити 1-5: Прості запити з одним-двома параметрами
   - Запити 6-8: Складні запити з агрегацією та M-to-M логікою

2. **4 аналітичні звіти** з розрахунками:
   - Звіт 1: Експедиції та дослідники
   - Звіт 2: Статистика лабораторій
   - Звіт 3: Контракти дослідників
   - Звіт 4: Огляд організацій

СТРУКТУРА ФУНКЦІЇ ЗАПИТУ:
def query_name(param1, param2=None):
    \"\"\"
    Запит N: Опис запиту (українською)
    Query: Description (English)
    
    Parameters:
        param1 (type): Опис параметра
        param2 (type): Опис параметра
    
    Returns:
        list: Список результатів запиту
    
    SQL: SELECT ... FROM ... WHERE ... (еквівалент SQL)
    \"\"\"
    return db.session.query(Model).filter(...).all()

ОСНОВНІ ОПЕРАЦІЇ SQLAlchemy:

1. SELECT все записи:
   db.session.query(Model).all()

2. WHERE з умовою:
   db.session.query(Model).filter(Model.field == value).all()

3. WHERE з LIKE (частковий збіг):
   db.session.query(Model).filter(Model.field.ilike('%text%')).all()

4. WHERE з BETWEEN:
   db.session.query(Model).filter(Model.field.between(min, max)).all()

5. WHERE з AND (кілька умов):
   db.session.query(Model).filter(
       and_(Model.field1 == value1, Model.field2 == value2)
   ).all()

6. WHERE з OR:
   db.session.query(Model).filter(
       or_(Model.field == value1, Model.field == value2)
   ).all()

7. INNER JOIN (об'єднання таблиць):
   db.session.query(Model1, Model2).join(Model2).filter(...).all()

8. LEFT JOIN (зовнішнє об'єднання):
   db.session.query(Model1).outerjoin(Model2).filter(...).all()

9. GROUP BY з агрегацією:
   db.session.query(Model.category, func.count(Model.id)).group_by(Model.category).all()

10. ORDER BY (сортування):
    db.session.query(Model).order_by(Model.field.asc()).all()  # за зростанням
    db.session.query(Model).order_by(Model.field.desc()).all()  # за спаданням

11. DISTINCT (унікальні записи):
    db.session.query(Model).distinct().all()

12. LIMIT/OFFSET (сторінкування):
    db.session.query(Model).limit(10).offset(0).all()  # Перші 10
    db.session.query(Model).limit(10).offset(10).all()  # Наступні 10

АГРЕГАЦІЙНІ ФУНКЦІЇ:
- func.count(Model.id)     → COUNT(*) - кількість записів
- func.sum(Model.field)    → SUM() - сума
- func.avg(Model.field)    → AVG() - середнє значення
- func.min(Model.field)    → MIN() - мінімум
- func.max(Model.field)    → MAX() - максимум

ВИТЯГ ДАТИ (EXTRACT):
- func.year(Model.date_field)   → Рік
- func.month(Model.date_field)  → Місяць
- func.day(Model.date_field)    → День

================================================================================
ЯК ДОДАТИ НОВИЙ ЗАПИТ:
================================================================================

1. Визначити вимоги запиту (параметри, умови, результат)

2. Написати функцію в queries.py:

def query_my_filter(param1, param2=None):
    \"\"\"
    Мій запит - MyQuery
    Query: Description
    
    Parameters:
        param1 (str): Перший параметр
        param2 (int): Другий параметр (опціональний)
    
    Returns:
        list: Список результатів
    \"\"\"
    query = db.session.query(Researcher).join(Laboratory)
    
    if param1:
        query = query.filter(Researcher.specialization.ilike(f'%{param1}%'))
    
    if param2:
        query = query.filter(Laboratory.num_employees > param2)
    
    return query.order_by(Researcher.full_name).all()

3. Додати маршрут в app.py (див. app.py документацію)

4. Додати форму в forms.py (див. forms.py документацію)

5. Додати HTML шаблон в templates/queries/ (див. приклади)

================================================================================
ЯК ПРАЦЮЄ ЛОГІКА ЗАПИТІВ:
================================================================================

1. ОТРИМАННЯ ФОРМИ (GET):
   /queries/query1  →  Показати форму для вводу параметрів

2. ВВЕДЕННЯ ПАРАМЕТРІВ (користувач):
   Користувач вводить значення параметрів

3. ВІДПРАВКА ФОРМИ (POST):
   Форма відправляється на сервер з параметрами

4. ВИКОНАННЯ ЗАПИТУ:
   results = query_name(param1, param2)  →  SQLAlchemy генерує SQL
                                          →  SQLite виконує запит
                                          →  Результати повертаються

5. ФОРМАТУВАННЯ РЕЗУЛЬТАТІВ:
   Результати обробляються та виводяться в HTML таблицю

6. ВІДОБРАЖЕННЯ (GET результатів):
   render_template('queries/results.html', results=results)

================================================================================
"""
from models import db, Director, Organization, Laboratory, Expedition, Role, Researcher, Equipment, Contract
from sqlalchemy import func, and_, or_
from datetime import datetime

# ============================================================================
# ПРОСТІ ПАРАМЕТРИЗОВАНІ ЗАПИТИ (Simple Parametrized Queries)
# ============================================================================

def query_researchers_by_specialization(specialization):
    """
    Запит 1: Дослідники за спеціалізацією
    Query: Researchers with specific specialization
    
    SQL: SELECT * FROM researchers WHERE specialization LIKE %specialization%
    """
    return db.session.query(Researcher).filter(
        Researcher.specialization.ilike(f'%{specialization}%')
    ).all()


def query_equipment_cost_above(min_cost):
    """
    Запит 2: Обладнання вартістю вище від заданої
    Query: Equipment with cost above specified value
    
    SQL: SELECT e.* FROM equipment e 
         JOIN laboratories l ON e.laboratory_id = l.id
         WHERE e.cost > %min_cost%
    """
    return db.session.query(Equipment, Laboratory).join(
        Laboratory
    ).filter(Equipment.cost > min_cost).all()


def query_expeditions_by_region_and_date(region, start_year):
    """
    Запит 3: Експедиції у регіоні починаючи з року
    Query: Expeditions in specific region and year range
    
    SQL: SELECT e.* FROM expeditions e
         WHERE e.region = %region% AND YEAR(e.start_date) >= %start_year%
    """
    from sqlalchemy import extract
    return db.session.query(Expedition).filter(
        and_(
            Expedition.region == region,
            extract('year', Expedition.start_date) >= start_year
        )
    ).all()


def query_contracts_by_budget_and_date(min_budget, end_year):
    """
    Запит 4: Контракти з бюджетом вище та років дії
    Query: Contracts with budget above and ending in specific year
    
    SQL: SELECT c.*, r.full_name, o.name FROM contracts c
         JOIN researchers r ON c.researcher_id = r.id
         JOIN organizations o ON c.organization_id = o.id
         WHERE c.budget > %min_budget% AND YEAR(c.end_date) = %end_year%
    """
    from sqlalchemy import extract
    return db.session.query(Contract, Researcher, Organization).join(
        Researcher, Contract.researcher_id == Researcher.id
    ).join(
        Organization, Contract.organization_id == Organization.id
    ).filter(
        and_(
            Contract.budget > min_budget,
            extract('year', Contract.end_date) == end_year
        )
    ).all()


def query_laboratories_by_employee_count(min_employees, max_employees):
    """
    Запит 5: Лабораторії за кількістю співробітників
    Query: Laboratories with specific employee count range
    
    SQL: SELECT l.*, o.name FROM laboratories l
         JOIN organizations o ON l.organization_id = o.id
         WHERE l.num_employees BETWEEN %min% AND %max%
    """
    return db.session.query(Laboratory, Organization).join(
        Organization
    ).filter(
        and_(
            Laboratory.num_employees >= min_employees,
            Laboratory.num_employees <= max_employees
        )
    ).all()


# ============================================================================
# ЗАПИТИ З МНОЖИННИМИ ПОРІВНЯННЯМИ (Queries with Multiple Comparisons)
# ============================================================================

def query_researchers_same_specialization_as(specialization):
    """
    Запит 6: Всі дослідники з такою ж спеціалізацією як вказана
    Query: All researchers with the same specialization as given parameter
    
    SQL: SELECT r1.* FROM researchers r1
         WHERE r1.specialization IN (
             SELECT r2.specialization FROM researchers r2 
             WHERE r2.specialization = %specialization%
         )
    """
    return db.session.query(Researcher).filter(
        Researcher.specialization == specialization
    ).all()


def query_researchers_all_expeditions():
    """
    Запит 7: Дослідники, що беруть участь у всіх експедиціях
    Query: Researchers participating in all expeditions
    
    SQL: SELECT r.* FROM researchers r
         WHERE NOT EXISTS (
             SELECT 1 FROM expeditions e
             WHERE NOT EXISTS (
                 SELECT 1 FROM expedition_researchers er
                 WHERE er.expedition_id = e.id AND er.researcher_id = r.id
             )
         )
    """
    # Get all expeditions count
    total_expeditions = db.session.query(func.count(Expedition.id)).scalar()
    
    # Get researchers who participate in all expeditions
    researcher_expedition_counts = db.session.query(
        Researcher.id,
        func.count(Expedition.id).label('exp_count')
    ).join(Expedition, Researcher.expeditions).group_by(Researcher.id).all()
    
    researcher_ids = [r[0] for r in researcher_expedition_counts if r[1] == total_expeditions]
    
    return db.session.query(Researcher).filter(Researcher.id.in_(researcher_ids)).all()


def query_researchers_same_laboratory(target_researcher_id):
    """
    Запит 8: Дослідники в одній лабораторії з конкретним дослідником
    Query: Pairs of researchers working in same laboratory with same specialization
    
    SQL: SELECT r1.*, r2.* FROM researchers r1, researchers r2
         WHERE r1.laboratory_id = r2.laboratory_id
         AND r1.specialization = r2.specialization
         AND r1.id != r2.id
    """
    target = db.session.query(Researcher).filter(
        Researcher.id == target_researcher_id
    ).first()
    
    if not target:
        return []
    
    return db.session.query(Researcher).filter(
        and_(
            Researcher.laboratory_id == target.laboratory_id,
            Researcher.specialization == target.specialization,
            Researcher.id != target.id
        )
    ).all()


# ============================================================================
# СКЛАДНІ ЗАПИТИ (Complex Queries)
# ============================================================================

def query_average_equipment_cost_by_lab():
    """
    Query: Average equipment cost per laboratory
    Returns: List of (Laboratory, average_cost)
    """
    return db.session.query(
        Laboratory,
        func.avg(Equipment.cost).label('avg_cost')
    ).join(Equipment).group_by(Laboratory.id).all()


def query_researchers_per_organization():
    """
    Query: Count of researchers per organization
    Returns: List of (Organization, researcher_count)
    """
    return db.session.query(
        Organization,
        func.count(Researcher.id).label('researcher_count')
    ).join(Laboratory).join(Researcher).group_by(Organization.id).all()


def query_active_contracts_by_organization(current_date=None):
    """
    Query: Active contracts (current date between start and end) grouped by organization
    Returns: List of (Organization, active_contract_count)
    """
    if current_date is None:
        from datetime import datetime
        current_date = datetime.now().date()
    
    return db.session.query(
        Organization,
        func.count(Contract.id).label('active_count')
    ).join(Contract).filter(
        and_(
            Contract.start_date <= current_date,
            Contract.end_date >= current_date
        )
    ).group_by(Organization.id).all()


# ============================================================================
# ЗВІТИ (Reports)
# ============================================================================

def get_report_expeditions_with_researchers():
    """
    ЗВІТ 1: Експедиції та кількість дослідників у кожній
    Report: Expeditions with researcher count
    """
    expeditions = db.session.query(Expedition).all()
    results = []
    for exp in expeditions:
        researcher_count = len(exp.researchers)
        # Calculate average experience (simplified - all same value for now)
        avg_experience = 5  # placeholder
        results.append((exp, researcher_count, avg_experience))
    return results


def get_report_lab_statistics():
    """
    ЗВІТ 2: Статистика лабораторій
    Report: Laboratory statistics with equipment count and total cost
    """
    labs = db.session.query(Laboratory).all()
    results = []
    for lab in labs:
        equipment_count = Equipment.query.filter_by(laboratory_id=lab.id).count()
        total_cost = db.session.query(func.sum(Equipment.cost)).filter_by(
            laboratory_id=lab.id
        ).scalar() or 0
        researcher_count = Researcher.query.filter_by(laboratory_id=lab.id).count()
        org = Organization.query.get(lab.organization_id)
        results.append((lab, org, equipment_count, total_cost, researcher_count))
    return results


def get_report_researcher_contracts():
    """
    ЗВІТ 3: Звіт про контракти дослідників
    Report: Researcher contracts with duration and budget
    """
    results = []
    contracts = db.session.query(Contract).all()
    for contract in contracts:
        researcher = Researcher.query.get(contract.researcher_id)
        role = Role.query.get(researcher.role_id) if researcher else None
        # Calculate duration in days using Python
        duration_days = (contract.end_date - contract.start_date).days
        budget_per_day = contract.budget / duration_days if duration_days > 0 else 0
        results.append((researcher, role, contract, duration_days, budget_per_day))
    return results


def get_report_organization_overview():
    """
    ЗВІТ 4: Огляд організацій
    Report: Organization overview with total budget, lab count, expedition count
    """
    results = []
    orgs = db.session.query(Organization).all()
    for org in orgs:
        director = Director.query.get(org.director_id)
        lab_count = Laboratory.query.filter_by(organization_id=org.id).count()
        # For expeditions, we need to join through directors
        exp_count = Expedition.query.filter_by(director_id=org.director_id).count()
        # For budget, sum all contracts for researchers in labs of this org
        lab_ids = [l.id for l in Laboratory.query.filter_by(organization_id=org.id).all()]
        researchers = db.session.query(Researcher).filter(Researcher.laboratory_id.in_(lab_ids)).all() if lab_ids else []
        researcher_ids = [r.id for r in researchers]
        total_budget = db.session.query(func.sum(Contract.budget)).filter(
            Contract.researcher_id.in_(researcher_ids)
        ).scalar() if researcher_ids else 0
        results.append((org, director, lab_count, exp_count, total_budget))
    return results
