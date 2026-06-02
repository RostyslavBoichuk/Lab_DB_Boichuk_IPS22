"""
================================================================================
ГОЛОВНА ПРОГРАМА ДОДАТКА (Main Application - app.py)
================================================================================

ПРИЗНАЧЕННЯ:
Центральний файл Flask додатка, який містить усі маршрути (routes) для 
CRUD операцій та обробки запитів до бази даних.

ФУНКЦІОНАЛ:
1. Ініціалізація Flask додатка та бази даних SQLite
2. Визначення маршрутів для:
   - Навігації по системі (головна сторінка, меню)
   - CRUD операцій для 8 сутностей (Directors, Organizations, Laboratories, тощо)
   - Виконання параметризованих запитів (8 запитів)
   - Генерування аналітичних звітів (4 звіти)
   - Управління M-to-M зв'язками (вибір множинних записів)
3. Обробка помилок (404, 500)
4. Валідація форм та збереження даних в БД

АРХІТЕКТУРА:
- HTTP методи: GET (отримання форми), POST (обробка форми)
- Шаблонізація: Jinja2 HTML шаблони в папці templates/
- ORM: SQLAlchemy для роботи з БД (див. models.py)
- Валідація: WTForms для валідації на рівні форм (див. forms.py)

КІЛЬКість МАРШРУТІВ: ~40+ маршрутів для всіх операцій

================================================================================
ЯК ДОДАТИ НОВИЙ МАРШРУТ:
================================================================================

1. Базовий маршрут (без форми):
   
   @app.route('/mypath')
   def my_function():
       \"\"\"Description\"\"\"
       return render_template('mytemplate.html')

2. Маршрут з додаванням запису (CRUD - Create):
   
   @app.route('/myentities/add', methods=['GET', 'POST'])
   def add_my_entity():
       form = MyEntityForm()
       form.foreign_key_field.choices = get_foreign_key_values()
       if form.validate_on_submit():
           entity = MyEntity(
               field1=form.field1.data,
               field2=form.field2.data
           )
           db.session.add(entity)
           db.session.commit()
           flash('Запис додано!', 'success')
           return redirect(url_for('list_my_entities'))
       return render_template('myentities/form.html', form=form)

3. Маршрут для редагування (CRUD - Update):
   
   @app.route('/myentities/<int:id>/edit', methods=['GET', 'POST'])
   def edit_my_entity(id):
       entity = MyEntity.query.get_or_404(id)
       form = MyEntityForm()
       if form.validate_on_submit():
           entity.field1 = form.field1.data
           entity.field2 = form.field2.data
           db.session.commit()
           flash('Запис оновлено!', 'success')
           return redirect(url_for('list_my_entities'))
       elif request.method == 'GET':
           form.field1.data = entity.field1
           form.field2.data = entity.field2
       return render_template('myentities/form.html', form=form)

4. Маршрут для видалення (CRUD - Delete):
   
   @app.route('/myentities/<int:id>/delete', methods=['POST'])
   def delete_my_entity(id):
       entity = MyEntity.query.get_or_404(id)
       db.session.delete(entity)
       db.session.commit()
       flash('Запис видалено!', 'success')
       return redirect(url_for('list_my_entities'))

5. Маршрут для виконання запиту:
   
   @app.route('/queries/myquery', methods=['GET', 'POST'])
   def my_query():
       if request.method == 'POST':
           param1 = request.form.get('param1')
           results = query_my_function(param1)
           return render_template('queries/myquery.html', results=results)
       return render_template('queries/myquery_form.html')

================================================================================
ЯК ПРАЦЮЄ ЛОГІКА:
================================================================================

1. REQUEST (HTTP запит від браузера):
   GET  /directors/add        → Показати форму для додавання
   POST /directors/add        → Обробити заповнену форму

2. ОБРОБКА ФОРМИ:
   - form.validate_on_submit() перевіряє WTForms валідацію
   - Якщо форма валідна, дані зберігаються в БД
   - Якщо форма невалідна, показується повідомлення про помилку

3. ЗБЕРЕЖЕННЯ В БД:
   db.session.add(entity)      → Додати новий запис
   db.session.commit()         → Зберегти зміни в БД

4. ВІДПОВІДЬ (HTML сторінка від сервера):
   redirect(url_for(...))      → Перенаправити на іншу сторінку
   render_template(...)        → Показати HTML шаблон

5. FLASH ПОВІДОМЛЕННЯ:
   flash('Текст повідомлення', 'success')  → Зелене повідомлення
   flash('Текст повідомлення', 'error')    → Червоне повідомлення

================================================================================
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, Director, Organization, Laboratory, Expedition, Role, Researcher, Equipment, Contract
from forms import (DirectorForm, OrganizationForm, LaboratoryForm, ExpeditionForm,
                   RoleForm, ResearcherForm, EquipmentForm, ContractForm)
from queries import *
import os

# ============================================================================
# СТВОРЕННЯ ДОДАТКА (Application Setup)
# ============================================================================

app = Flask(__name__)
app.config.from_object(Config)

# Ініціалізація бази даних
db.init_app(app)

with app.app_context():
    db.create_all()


# ============================================================================
# ДОПОМІЖНІ ФУНКЦІЇ (Helper Functions)
# ============================================================================

def get_directors():
    """Get all directors for select fields"""
    return [(d.id, d.full_name) for d in Director.query.all()]


def get_organizations():
    """Get all organizations for select fields"""
    return [(o.id, o.name) for o in Organization.query.all()]


def get_laboratories():
    """Get all laboratories for select fields"""
    return [(l.id, l.name) for l in Laboratory.query.all()]


def get_roles():
    """Get all roles for select fields"""
    return [(r.id, r.name) for r in Role.query.all()]


def get_researchers():
    """Get all researchers for select fields - returns list of (id, name) tuples"""
    researchers = Researcher.query.all()
    result = []
    for r in researchers:
        if r.id and r.full_name:
            result.append((str(r.id), str(r.full_name)))
    return result


def get_expedition_organizations(expedition_id):
    """Get organizations that finance a specific expedition"""
    expedition = Expedition.query.get(expedition_id)
    return expedition.organizations if expedition else []


def get_expedition_equipment(expedition_id):
    """Get equipment used in a specific expedition"""
    expedition = Expedition.query.get(expedition_id)
    return expedition.equipment if expedition else []


def get_researcher_equipment(researcher_id):
    """Get equipment used by a specific researcher"""
    researcher = Researcher.query.get(researcher_id)
    return researcher.equipment if researcher else []


# ============================================================================
# НАВІГАЦІЙНІ ФУНКЦІЇ (Navigation Helper Functions)
# ============================================================================

def get_record_navigation(model_class, current_id, id_column=None):
    """Get previous and next record IDs for form navigation"""
    if id_column is None:
        id_column = model_class.id
    
    all_records = db.session.query(id_column).order_by(id_column).all()
    all_ids = [r[0] for r in all_records]
    
    if current_id not in all_ids:
        return None, None
    
    idx = all_ids.index(current_id)
    prev_id = all_ids[idx - 1] if idx > 0 else None
    next_id = all_ids[idx + 1] if idx < len(all_ids) - 1 else None
    
    return prev_id, next_id


def get_choice_display(value, choices):
    """Get display text for a choice value"""
    for choice_value, choice_text in choices:
        if choice_value == value:
            return choice_text
    return str(value)


# ============================================================================
# МАРШРУТИ - ГОЛОВНА СТОРІНКА (Routes - Main Menu)
# ============================================================================

@app.route('/')
@app.route('/index')
def index():
    """Main menu page"""
    return render_template('index.html')


# ============================================================================
# МАРШРУТИ - ДИРЕКТОРИ (Routes - Directors)
# ============================================================================

@app.route('/directors')
def list_directors():
    """List all directors"""
    directors = Director.query.all()
    return render_template('directors/list.html', directors=directors)


@app.route('/directors/add', methods=['GET', 'POST'])
def add_director():
    """Add new director"""
    form = DirectorForm()
    if form.validate_on_submit():
        director = Director(
            full_name=form.full_name.data,
            appointment_date=form.appointment_date.data
        )
        db.session.add(director)
        db.session.commit()
        flash('Директор додано успішно!', 'success')
        return redirect(url_for('list_directors'))
    return render_template('directors/form.html', form=form, title='Додати директора')


@app.route('/directors/<int:id>/edit', methods=['GET', 'POST'])
def edit_director(id):
    """Edit director"""
    director = Director.query.get_or_404(id)
    form = DirectorForm()
    if form.validate_on_submit():
        director.full_name = form.full_name.data
        director.appointment_date = form.appointment_date.data
        db.session.commit()
        flash('Директор оновлено!', 'success')
        return redirect(url_for('list_directors'))
    elif request.method == 'GET':
        form.full_name.data = director.full_name
        form.appointment_date.data = director.appointment_date
    
    # Navigation
    prev_id, next_id = get_record_navigation(Director, id)
    
    return render_template('directors/form.html', form=form, title='Редагувати директора',
                         record=director, prev_id=prev_id, next_id=next_id, edit=True)


@app.route('/directors/<int:id>/delete', methods=['POST'])
def delete_director(id):
    """Delete director"""
    director = Director.query.get_or_404(id)
    db.session.delete(director)
    db.session.commit()
    flash('Директор видалено!', 'success')
    return redirect(url_for('list_directors'))


# ============================================================================
# МАРШРУТИ - ОРГАНІЗАЦІЇ (Routes - Organizations)
# ============================================================================

@app.route('/organizations')
def list_organizations():
    """List all organizations"""
    organizations = Organization.query.all()
    return render_template('organizations/list.html', organizations=organizations)


@app.route('/organizations/add', methods=['GET', 'POST'])
def add_organization():
    """Add new organization"""
    form = OrganizationForm()
    form.director_id.choices = get_directors()
    if form.validate_on_submit():
        organization = Organization(
            id=form.id.data,
            name=form.name.data,
            country=form.country.data,
            year_founded=form.year_founded.data,
            director_id=form.director_id.data
        )
        db.session.add(organization)
        db.session.commit()
        flash('Організація додана успішно!', 'success')
        return redirect(url_for('list_organizations'))
    return render_template('organizations/form.html', form=form, title='Додати організацію')


@app.route('/organizations/<id>/edit', methods=['GET', 'POST'])
def edit_organization(id):
    """Edit organization"""
    organization = Organization.query.get_or_404(id)
    form = OrganizationForm()
    form.director_id.choices = get_directors()
    if form.validate_on_submit():
        organization.name = form.name.data
        organization.country = form.country.data
        organization.year_founded = form.year_founded.data
        organization.director_id = form.director_id.data
        db.session.commit()
        flash('Організація оновлена!', 'success')
        return redirect(url_for('list_organizations'))
    elif request.method == 'GET':
        form.id.data = organization.id
        form.name.data = organization.name
        form.country.data = organization.country
        form.year_founded.data = organization.year_founded
        form.director_id.data = organization.director_id
    
    # Navigation
    prev_id, next_id = get_record_navigation(Organization, id, Organization.id)
    
    return render_template('organizations/form.html', form=form, title='Редагувати організацію',
                         record=organization, prev_id=prev_id, next_id=next_id, edit=True,
                         director_display=get_choice_display(organization.director_id, get_directors()))


@app.route('/organizations/<id>/delete', methods=['POST'])
def delete_organization(id):
    """Delete organization"""
    organization = Organization.query.get_or_404(id)
    db.session.delete(organization)
    db.session.commit()
    flash('Організація видалена!', 'success')
    return redirect(url_for('list_organizations'))


# ============================================================================
# МАРШРУТИ - ЛАБОРАТОРІЇ (Routes - Laboratories)
# ============================================================================

@app.route('/laboratories')
def list_laboratories():
    """List all laboratories"""
    laboratories = Laboratory.query.all()
    return render_template('laboratories/list.html', laboratories=laboratories)


@app.route('/laboratories/add', methods=['GET', 'POST'])
def add_laboratory():
    """Add new laboratory"""
    form = LaboratoryForm()
    form.organization_id.choices = get_organizations()
    if form.validate_on_submit():
        laboratory = Laboratory(
            name=form.name.data,
            num_employees=form.num_employees.data,
            activities=form.activities.data,
            organization_id=form.organization_id.data
        )
        db.session.add(laboratory)
        db.session.commit()
        flash('Лабораторія додана успішно!', 'success')
        return redirect(url_for('list_laboratories'))
    return render_template('laboratories/form.html', form=form, title='Додати лабораторію')


@app.route('/laboratories/<int:id>/edit', methods=['GET', 'POST'])
def edit_laboratory(id):
    """Edit laboratory"""
    laboratory = Laboratory.query.get_or_404(id)
    form = LaboratoryForm()
    form.organization_id.choices = get_organizations()
    if form.validate_on_submit():
        laboratory.name = form.name.data
        laboratory.num_employees = form.num_employees.data
        laboratory.activities = form.activities.data
        laboratory.organization_id = form.organization_id.data
        db.session.commit()
        flash('Лабораторія оновлена!', 'success')
        return redirect(url_for('list_laboratories'))
    elif request.method == 'GET':
        form.name.data = laboratory.name
        form.num_employees.data = laboratory.num_employees
        form.activities.data = laboratory.activities
        form.organization_id.data = laboratory.organization_id
    
    # Navigation
    prev_id, next_id = get_record_navigation(Laboratory, id)
    
    return render_template('laboratories/form.html', form=form, title='Редагувати лабораторію',
                         record=laboratory, prev_id=prev_id, next_id=next_id, edit=True,
                         org_display=get_choice_display(laboratory.organization_id, get_organizations()))


@app.route('/laboratories/<int:id>/delete', methods=['POST'])
def delete_laboratory(id):
    """Delete laboratory"""
    laboratory = Laboratory.query.get_or_404(id)
    db.session.delete(laboratory)
    db.session.commit()
    flash('Лабораторія видалена!', 'success')
    return redirect(url_for('list_laboratories'))


# ============================================================================
# МАРШРУТИ - ЕКСПЕДИЦІЇ (Routes - Expeditions)
# ============================================================================

@app.route('/expeditions')
def list_expeditions():
    """List all expeditions"""
    expeditions = Expedition.query.all()
    return render_template('expeditions/list.html', expeditions=expeditions)


@app.route('/expeditions/add', methods=['GET', 'POST'])
def add_expedition():
    """Add new expedition"""
    form = ExpeditionForm()
    form.director_id.choices = get_directors()
    if form.validate_on_submit():
        expedition = Expedition(
            id=form.id.data,
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            region=form.region.data,
            director_id=form.director_id.data
        )
        db.session.add(expedition)
        db.session.commit()
        flash('Експедиція додана успішно!', 'success')
        return redirect(url_for('list_expeditions'))
    return render_template('expeditions/form.html', form=form, title='Додати експедицію')


@app.route('/expeditions/<id>/edit', methods=['GET', 'POST'])
def edit_expedition(id):
    """Edit expedition"""
    expedition = Expedition.query.get_or_404(id)
    form = ExpeditionForm()
    form.director_id.choices = get_directors()
    if form.validate_on_submit():
        expedition.name = form.name.data
        expedition.start_date = form.start_date.data
        expedition.end_date = form.end_date.data
        expedition.region = form.region.data
        expedition.director_id = form.director_id.data
        db.session.commit()
        flash('Експедиція оновлена!', 'success')
        return redirect(url_for('list_expeditions'))
    elif request.method == 'GET':
        form.id.data = expedition.id
        form.name.data = expedition.name
        form.start_date.data = expedition.start_date
        form.end_date.data = expedition.end_date
        form.region.data = expedition.region
        form.director_id.data = expedition.director_id
    
    # Navigation
    prev_id, next_id = get_record_navigation(Expedition, id, Expedition.id)
    
    return render_template('expeditions/form.html', form=form, title='Редагувати експедицію',
                         record=expedition, prev_id=prev_id, next_id=next_id, edit=True,
                         director_display=get_choice_display(expedition.director_id, get_directors()))


@app.route('/expeditions/<id>/delete', methods=['POST'])
def delete_expedition(id):
    """Delete expedition"""
    expedition = Expedition.query.get_or_404(id)
    db.session.delete(expedition)
    db.session.commit()
    flash('Експедиція видалена!', 'success')
    return redirect(url_for('list_expeditions'))


# ============================================================================
# МАРШРУТИ - РОЛІ (Routes - Roles)
# ============================================================================

@app.route('/roles')
def list_roles():
    """List all roles"""
    roles = Role.query.all()
    return render_template('roles/list.html', roles=roles)


@app.route('/roles/add', methods=['GET', 'POST'])
def add_role():
    """Add new role"""
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(role)
        db.session.commit()
        flash('Роль додана успішно!', 'success')
        return redirect(url_for('list_roles'))
    return render_template('roles/form.html', form=form, title='Додати роль')


@app.route('/roles/<int:id>/edit', methods=['GET', 'POST'])
def edit_role(id):
    """Edit role"""
    role = Role.query.get_or_404(id)
    form = RoleForm()
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.commit()
        flash('Роль оновлена!', 'success')
        return redirect(url_for('list_roles'))
    elif request.method == 'GET':
        form.name.data = role.name
        form.description.data = role.description
    
    # Navigation
    prev_id, next_id = get_record_navigation(Role, id)
    
    return render_template('roles/form.html', form=form, title='Редагувати роль',
                         record=role, prev_id=prev_id, next_id=next_id, edit=True)


@app.route('/roles/<int:id>/delete', methods=['POST'])
def delete_role(id):
    """Delete role"""
    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('Роль видалена!', 'success')
    return redirect(url_for('list_roles'))


# ============================================================================
# МАРШРУТИ - ДОСЛІДНИКИ (Routes - Researchers)
# ============================================================================

@app.route('/researchers')
def list_researchers():
    """List all researchers"""
    researchers = Researcher.query.all()
    return render_template('researchers/list.html', researchers=researchers)


@app.route('/researchers/add', methods=['GET', 'POST'])
def add_researcher():
    """Add new researcher"""
    form = ResearcherForm()
    form.role_id.choices = get_roles()
    form.laboratory_id.choices = get_laboratories()
    form.supervisor_id.choices = [(0, 'Немає')] + get_researchers()
    if form.validate_on_submit():
        researcher = Researcher(
            id=form.id.data,
            full_name=form.full_name.data,
            specialization=form.specialization.data,
            hire_date=form.hire_date.data,
            role_id=form.role_id.data,
            laboratory_id=form.laboratory_id.data,
            supervisor_id=form.supervisor_id.data if form.supervisor_id.data != 0 else None
        )
        db.session.add(researcher)
        db.session.commit()
        flash('Дослідник додан успішно!', 'success')
        return redirect(url_for('list_researchers'))
    return render_template('researchers/form.html', form=form, title='Додати дослідника')


@app.route('/researchers/<id>/edit', methods=['GET', 'POST'])
def edit_researcher(id):
    """Edit researcher"""
    researcher = Researcher.query.get_or_404(id)
    form = ResearcherForm()
    form.role_id.choices = get_roles()
    form.laboratory_id.choices = get_laboratories()
    form.supervisor_id.choices = [(0, 'Немає')] + get_researchers()
    if form.validate_on_submit():
        researcher.full_name = form.full_name.data
        researcher.specialization = form.specialization.data
        researcher.hire_date = form.hire_date.data
        researcher.role_id = form.role_id.data
        researcher.laboratory_id = form.laboratory_id.data
        researcher.supervisor_id = form.supervisor_id.data if form.supervisor_id.data != 0 else None
        db.session.commit()
        flash('Дослідник оновлено!', 'success')
        return redirect(url_for('list_researchers'))
    elif request.method == 'GET':
        form.id.data = researcher.id
        form.full_name.data = researcher.full_name
        form.specialization.data = researcher.specialization
        form.hire_date.data = researcher.hire_date
        form.role_id.data = researcher.role_id
        form.laboratory_id.data = researcher.laboratory_id
        form.supervisor_id.data = researcher.supervisor_id
    
    # Navigation
    prev_id, next_id = get_record_navigation(Researcher, id, Researcher.id)
    
    return render_template('researchers/form.html', form=form, title='Редагувати дослідника',
                         record=researcher, prev_id=prev_id, next_id=next_id, edit=True,
                         role_display=get_choice_display(researcher.role_id, get_roles()),
                         lab_display=get_choice_display(researcher.laboratory_id, get_laboratories()),
                         supervisor_display=get_choice_display(researcher.supervisor_id, [(0, 'Немає')] + get_researchers()) if researcher.supervisor_id else 'Немає')


@app.route('/researchers/<id>/delete', methods=['POST'])
def delete_researcher(id):
    """Delete researcher"""
    researcher = Researcher.query.get_or_404(id)
    db.session.delete(researcher)
    db.session.commit()
    flash('Дослідник видалено!', 'success')
    return redirect(url_for('list_researchers'))


# ============================================================================
# МАРШРУТИ - ОБЛАДНАННЯ (Routes - Equipment)
# ============================================================================

@app.route('/equipment')
def list_equipment():
    """List all equipment"""
    equipment = Equipment.query.all()
    return render_template('equipment/list.html', equipment=equipment)


@app.route('/equipment/add', methods=['GET', 'POST'])
def add_equipment():
    """Add new equipment"""
    form = EquipmentForm()
    form.laboratory_id.choices = get_laboratories()
    if form.validate_on_submit():
        equip = Equipment(
            name=form.name.data,
            equipment_type=form.equipment_type.data,
            cost=form.cost.data,
            purchase_date=form.purchase_date.data,
            laboratory_id=form.laboratory_id.data
        )
        db.session.add(equip)
        db.session.commit()
        flash('Обладнання додано успішно!', 'success')
        return redirect(url_for('list_equipment'))
    return render_template('equipment/form.html', form=form, title='Додати обладнання')


@app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
def edit_equipment(id):
    """Edit equipment"""
    equip = Equipment.query.get_or_404(id)
    form = EquipmentForm()
    form.laboratory_id.choices = get_laboratories()
    if form.validate_on_submit():
        equip.name = form.name.data
        equip.equipment_type = form.equipment_type.data
        equip.cost = form.cost.data
        equip.purchase_date = form.purchase_date.data
        equip.laboratory_id = form.laboratory_id.data
        db.session.commit()
        flash('Обладнання оновлено!', 'success')
        return redirect(url_for('list_equipment'))
    elif request.method == 'GET':
        form.name.data = equip.name
        form.equipment_type.data = equip.equipment_type
        form.cost.data = equip.cost
        form.purchase_date.data = equip.purchase_date
        form.laboratory_id.data = equip.laboratory_id
    
    # Navigation
    prev_id, next_id = get_record_navigation(Equipment, id)
    
    return render_template('equipment/form.html', form=form, title='Редагувати обладнання',
                         record=equip, prev_id=prev_id, next_id=next_id, edit=True,
                         lab_display=get_choice_display(equip.laboratory_id, get_laboratories()))


@app.route('/equipment/<int:id>/delete', methods=['POST'])
def delete_equipment(id):
    """Delete equipment"""
    equip = Equipment.query.get_or_404(id)
    db.session.delete(equip)
    db.session.commit()
    flash('Обладнання видалено!', 'success')
    return redirect(url_for('list_equipment'))


# ============================================================================
# МАРШРУТИ - КОНТРАКТИ (Routes - Contracts)
# ============================================================================

@app.route('/contracts')
def list_contracts():
    """List all contracts"""
    contracts = Contract.query.all()
    return render_template('contracts/list.html', contracts=contracts)


@app.route('/contracts/add', methods=['GET', 'POST'])
def add_contract():
    """Add new contract"""
    form = ContractForm()
    form.researcher_id.choices = get_researchers()
    form.organization_id.choices = get_organizations()
    if form.validate_on_submit():
        contract = Contract(
            id=form.id.data,
            title=form.title.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            researcher_id=form.researcher_id.data,
            organization_id=form.organization_id.data
        )
        db.session.add(contract)
        db.session.commit()
        flash('Контракт додан успішно!', 'success')
        return redirect(url_for('list_contracts'))
    return render_template('contracts/form.html', form=form, title='Додати контракт')


@app.route('/contracts/<id>/edit', methods=['GET', 'POST'])
def edit_contract(id):
    """Edit contract"""
    contract = Contract.query.get_or_404(id)
    form = ContractForm()
    form.researcher_id.choices = get_researchers()
    form.organization_id.choices = get_organizations()
    if form.validate_on_submit():
        contract.title = form.title.data
        contract.start_date = form.start_date.data
        contract.end_date = form.end_date.data
        contract.budget = form.budget.data
        contract.researcher_id = form.researcher_id.data
        contract.organization_id = form.organization_id.data
        db.session.commit()
        flash('Контракт оновлено!', 'success')
        return redirect(url_for('list_contracts'))
    elif request.method == 'GET':
        form.id.data = contract.id
        form.title.data = contract.title
        form.start_date.data = contract.start_date
        form.end_date.data = contract.end_date
        form.budget.data = contract.budget
        form.researcher_id.data = contract.researcher_id
        form.organization_id.data = contract.organization_id
    
    # Navigation
    prev_id, next_id = get_record_navigation(Contract, id, Contract.id)
    
    return render_template('contracts/form.html', form=form, title='Редагувати контракт',
                         record=contract, prev_id=prev_id, next_id=next_id, edit=True,
                         researcher_display=get_choice_display(contract.researcher_id, get_researchers()),
                         org_display=get_choice_display(contract.organization_id, get_organizations()))


@app.route('/contracts/<id>/delete', methods=['POST'])
def delete_contract(id):
    """Delete contract"""
    contract = Contract.query.get_or_404(id)
    db.session.delete(contract)
    db.session.commit()
    flash('Контракт видалено!', 'success')
    return redirect(url_for('list_contracts'))


# ============================================================================
# МАРШРУТИ - ЗАПИТИ (Routes - Queries)
# ============================================================================

@app.route('/queries')
def queries_menu():
    """Queries menu page"""
    return render_template('queries/menu.html')


@app.route('/queries/1', methods=['GET', 'POST'])
def query1():
    """Запит 1: Дослідники за спеціалізацією"""
    results = []
    if request.method == 'POST':
        specialization = request.form.get('specialization')
        results = query_researchers_by_specialization(specialization)
    return render_template('queries/query1.html', results=results, 
                         title='Запит 1: Дослідники за спеціалізацією')


@app.route('/queries/2', methods=['GET', 'POST'])
def query2():
    """Запит 2: Обладнання вартістю вище від заданої"""
    results = []
    if request.method == 'POST':
        min_cost = float(request.form.get('min_cost'))
        results = query_equipment_cost_above(min_cost)
    return render_template('queries/query2.html', results=results,
                         title='Запит 2: Обладнання вартістю вище від заданої')


@app.route('/queries/3', methods=['GET', 'POST'])
def query3():
    """Запит 3: Експедиції у регіоні починаючи з року"""
    results = []
    if request.method == 'POST':
        region = request.form.get('region')
        start_year = int(request.form.get('start_year'))
        results = query_expeditions_by_region_and_date(region, start_year)
    return render_template('queries/query3.html', results=results,
                         title='Запит 3: Експедиції у регіоні')


@app.route('/queries/4', methods=['GET', 'POST'])
def query4():
    """Запит 4: Контракти з бюджетом та років дії"""
    results = []
    if request.method == 'POST':
        min_budget = float(request.form.get('min_budget'))
        end_year = int(request.form.get('end_year'))
        results = query_contracts_by_budget_and_date(min_budget, end_year)
    return render_template('queries/query4.html', results=results,
                         title='Запит 4: Контракти з бюджетом')


@app.route('/queries/5', methods=['GET', 'POST'])
def query5():
    """Запит 5: Лабораторії за кількістю співробітників"""
    results = []
    if request.method == 'POST':
        min_emps = int(request.form.get('min_employees'))
        max_emps = int(request.form.get('max_employees'))
        results = query_laboratories_by_employee_count(min_emps, max_emps)
    return render_template('queries/query5.html', results=results,
                         title='Запит 5: Лабораторії за кількістю')


@app.route('/queries/6')
def query6():
    """Запит 6: Дослідники з контрактами У ВСІХ організаціях"""
    results = query_researchers_contracts_with_all_organizations()
    return render_template('queries/query6.html', results=results,
                         title='Запит 6: Дослідники з контрактами У ВСІХ організаціях')


@app.route('/queries/7')
def query7():
    """Запит 7: Дослідники у всіх експедиціях"""
    results = query_researchers_all_expeditions()
    return render_template('queries/query7.html', results=results,
                         title='Запит 7: Дослідники у всіх експедиціях')


@app.route('/queries/8')
def query8():
    """Запит 8: Експедиції з дослідниками ВСІХ спеціалізацій"""
    results = query_expeditions_with_all_specializations()
    return render_template('queries/query8.html', results=results,
                         title='Запит 8: Експедиції з дослідниками ВСІХ спеціалізацій')


# ============================================================================
# МАРШРУТИ - ЗВІТИ (Routes - Reports)
# ============================================================================

@app.route('/reports')
def reports_menu():
    """Reports menu page"""
    return render_template('reports/menu.html')


@app.route('/reports/1')
def report1():
    """Звіт 1: Експедиції та кількість дослідників"""
    results = get_report_expeditions_with_researchers()
    return render_template('reports/report1.html', results=results,
                         title='Звіт 1: Експедиції та дослідники')


@app.route('/reports/2')
def report2():
    """Звіт 2: Статистика лабораторій"""
    results = get_report_lab_statistics()
    return render_template('reports/report2.html', results=results,
                         title='Звіт 2: Статистика лабораторій')


@app.route('/reports/3')
def report3():
    """Звіт 3: Контракти дослідників"""
    results = get_report_researcher_contracts()
    return render_template('reports/report3.html', results=results,
                         title='Звіт 3: Контракти дослідників')


@app.route('/reports/4')
def report4():
    """Звіт 4: Огляд організацій"""
    results = get_report_organization_overview()
    return render_template('reports/report4.html', results=results,
                         title='Звіт 4: Огляд організацій')


# ============================================================================
# МАРШРУТИ - M-to-M зв'язки (Routes - Many-to-Many Relationships)
# ============================================================================

@app.route('/api/expedition/<expedition_id>/organizations', methods=['GET'])
def get_expedition_organizations_api(expedition_id):
    """Get organizations financing an expedition"""
    expedition = Expedition.query.get_or_404(expedition_id)
    return jsonify({
        'organizations': [
            {'id': o.id, 'name': o.name} 
            for o in expedition.organizations
        ]
    })


@app.route('/api/expedition/<expedition_id>/equipment', methods=['GET'])
def get_expedition_equipment_api(expedition_id):
    """Get equipment used in an expedition"""
    expedition = Expedition.query.get_or_404(expedition_id)
    return jsonify({
        'equipment': [
            {'id': e.id, 'name': e.name, 'type': e.equipment_type}
            for e in expedition.equipment
        ]
    })


@app.route('/api/researcher/<researcher_id>/equipment', methods=['GET'])
def get_researcher_equipment_api(researcher_id):
    """Get equipment used by a researcher"""
    researcher = Researcher.query.get_or_404(researcher_id)
    return jsonify({
        'equipment': [
            {'id': e.id, 'name': e.name, 'cost': e.cost}
            for e in researcher.equipment
        ]
    })


# ============================================================================
# ОБРОБКА ПОМИЛОК (Error Handling)
# ============================================================================

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500


# ============================================================================
# ЗАПУСК ДОДАТКА (Application Launch)
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='localhost', port=5000)
