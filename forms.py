"""
================================================================================
ФОРМИ ДЛЯ ВАЛІДАЦІЇ ДАНИХ (Forms - forms.py)
================================================================================

ПРИЗНАЧЕННЯ:
Визначення WTForms для валідації та обробки даних, які користувач вводить 
через HTML форми. Кожна форма представляє одну таблицю або M-to-M зв'язок.

ФУНКЦІОНАЛ:
1. **8 форм для основних сутностей** (CRUD операції):
   - DirectorForm         → Додавання/редагування Директорів
   - OrganizationForm     → Додавання/редагування Організацій
   - LaboratoryForm       → Додавання/редагування Лабораторій
   - ExpeditionForm       → Додавання/редагування Експедицій
   - RoleForm            → Додавання/редагування Ролей
   - ResearcherForm      → Додавання/редагування Дослідників
   - EquipmentForm       → Додавання/редагування Обладнання
   - ContractForm        → Додавання/редагування Контрактів

2. **3 форми для M-to-M зв'язків** (вибір множинних записів):
   - ExpeditionOrganizationsForm  → Вибір організацій для експедиції
   - ExpeditionEquipmentForm      → Вибір обладнання для експедиції
   - ResearcherEquipmentForm      → Вибір обладнання для дослідника

3. **Валідація даних** перед збереженням в БД:
   - Обов'язкові поля (DataRequired)
   - Довжина рядка (Length)
   - Унікальність (Unique)
   - Опціональні поля (Optional)

СТРУКТУРА ФОРМИ:
class MyForm(FlaskForm):
    field1 = StringField('Назва поля', validators=[DataRequired(), Length(min=3)])
    field2 = IntegerField('Число', validators=[DataRequired()])
    field3 = SelectField('Вибір', validators=[DataRequired()])
    field4 = DateField('Дата', validators=[DataRequired()])
    submit = SubmitField('Зберегти')

ТИПИ ПОЛІВ WTForms:
- StringField           → Текстове поле
- IntegerField          → Числове поле (без дробу)
- FloatField            → Числове поле (з дробом)
- TextAreaField         → Багаторядковий текст
- DateField             → Датаване поле (YYYY-MM-DD)
- DateTimeField         → Дата та час
- BooleanField          → Checkbox (True/False)
- SelectField           → Dropdown (один вибір)
- SelectMultipleField   → Multiple select (кілька виборів)
- SubmitField           → Кнопка "Зберегти"

ВАЛІДАТОРИ WTForms:
- DataRequired()                    → Поле обов'язкове
- Optional()                        → Поле опціональне (може бути пустим)
- Length(min=3, max=100)           → Довжина від 3 до 100 символів
- Email()                          → Перевірка email формату
- EqualTo('password')              → Порівняння з іншим полем
- Regexp('^[A-Z]')                 → Регулярний вираз
- URL()                            → Перевірка URL
- NumberRange(min=0, max=100)      → Діапазон чисел

АТРИБУТИ ФОРМИ:
- form.field_name.data      → Значення поля (введене користувачем)
- form.field_name.errors    → Список помилок валідації
- form.field_name.label     → Назва поля (для HTML <label>)
- form.hidden_tag()         → CSRF токен для захисту від атак

================================================================================
ЯК ДОДАТИ НОВУ ФОРМУ:
================================================================================

1. Базова форма для CRUD операцій:

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class MyEntityForm(FlaskForm):
    \"\"\"Form for MyEntity data entry\"\"\"
    
    # Текстове поле - обов'язкове, 3-100 символів
    name = StringField('Назва', validators=[DataRequired(), Length(min=3, max=100)])
    
    # Числове поле - обов'язкове
    count = IntegerField('Кількість', validators=[DataRequired()])
    
    # Датаване поле - обов'язкове
    created_date = DateField('Дата створення', validators=[DataRequired()])
    
    # Dropdown - обов'язковий вибір
    category_id = SelectField('Категорія', coerce=int, validators=[DataRequired()])
    
    # Опціональний текст
    description = StringField('Опис', validators=[Optional(), Length(max=500)])
    
    # Кнопка відправки
    submit = SubmitField('Зберегти')

2. У app.py заповнити dropdown'и перед обробкою форми:

@app.route('/myentities/add', methods=['GET', 'POST'])
def add_my_entity():
    form = MyEntityForm()
    
    # Заповнити dropdown зі списку категорій
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        # Обробити форму...
    return render_template('myentities/form.html', form=form)

3. Обов'язкове додати @app.secret_key у config.py для CSRF захисту

================================================================================
ЯК ПРАЦЮЄ ЛОГІКА:
================================================================================

1. ОТРИМАННЯ ФОРМИ (GET запит):
   /directors/add  →  Сервер відправляє пусту форму

2. ЗАПОВНЕННЯ ФОРМИ (користувач вводить дані):
   Користувач клацає, вводить текст, вибирає з dropdown'ів

3. ВІДПРАВКА ФОРМИ (POST запит):
   Користувач клацає кнопку "Зберегти"  →  Дані відправляються на сервер

4. ВАЛІДАЦІЯ НА СЕРВЕРІ:
   form.validate_on_submit()  →  Перевіряються усі валідатори
   Якщо помилка  →  Форма заново показується з повідомленням про помилку
   Якщо OK       →  Дані обробляються та зберігаються в БД

5. ПЕРЕНАПРАВЛЕННЯ:
   Після збереження  →  redirect(url_for(...))  →  Перенаправлення на список

6. DROPDOWN НАСЕЛЕННЯ (SelectField):
   form.field.choices = [(value, display_text), ...]
   Приклад:
   form.director_id.choices = [(1, 'Петренко'), (2, 'Коваль')]
   ↓
   HTML: <option value="1">Петренко</option>

7. CSRF ЗАХИСТ:
   {{ form.hidden_tag() }}  →  Автоматично вставляє CSRF токен
   Flask перевіряє токен при POST запиті

================================================================================
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SubmitField, SelectField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional

# ============================================================================
# ФОРМИ ДЛЯ ВВОДУ ДАНИХ (Forms for Data Entry)
# ============================================================================

class DirectorForm(FlaskForm):
    """Form for Director data entry"""
    full_name = StringField('Повне імя (ПІБ)', validators=[DataRequired(), Length(min=3, max=255)])
    appointment_date = DateField('Дата призначення', validators=[DataRequired()])
    submit = SubmitField('Зберегти')


class OrganizationForm(FlaskForm):
    """Form for Organization data entry"""
    id = StringField('Ідентифікатор', validators=[DataRequired(), Length(min=1, max=50)])
    name = StringField('Назва організації', validators=[DataRequired(), Length(min=3, max=255)])
    country = StringField('Країна', validators=[DataRequired(), Length(min=2, max=100)])
    year_founded = IntegerField('Рік заснування', validators=[DataRequired()])
    director_id = SelectField('Директор', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Зберегти')


class LaboratoryForm(FlaskForm):
    """Form for Laboratory data entry"""
    name = StringField('Назва лабораторії', validators=[DataRequired(), Length(min=3, max=255)])
    num_employees = IntegerField('Кількість співробітників', validators=[DataRequired()])
    activities = TextAreaField('Напрями діяльності', validators=[Optional()])
    organization_id = SelectField('Організація', validators=[DataRequired()])
    submit = SubmitField('Зберегти')


class ExpeditionForm(FlaskForm):
    """Form for Expedition data entry"""
    id = StringField('Індекс експедиції', validators=[DataRequired(), Length(min=1, max=50)])
    name = StringField('Назва експедиції', validators=[DataRequired(), Length(min=3, max=255)])
    start_date = DateField('Дата початку', validators=[DataRequired()])
    end_date = DateField('Дата закінчення', validators=[DataRequired()])
    region = StringField('Регіон', validators=[DataRequired(), Length(min=2, max=100)])
    director_id = SelectField('Директор', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Зберегти')


class RoleForm(FlaskForm):
    """Form for Role data entry"""
    name = StringField('Назва ролі', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Опис ролі', validators=[Optional()])
    submit = SubmitField('Зберегти')


class ResearcherForm(FlaskForm):
    """Form for Researcher data entry"""
    id = StringField('ID дослідника', validators=[DataRequired(), Length(min=1, max=50)])
    full_name = StringField('Повне імя (ПІБ)', validators=[DataRequired(), Length(min=3, max=255)])
    specialization = StringField('Спеціалізація', validators=[Optional(), Length(max=255)])
    hire_date = DateField('Дата прийняття на роботу', validators=[DataRequired()])
    role_id = SelectField('Роль', coerce=int, validators=[DataRequired()])
    laboratory_id = SelectField('Лабораторія', coerce=int, validators=[DataRequired()])
    supervisor_id = SelectField('Керівник', coerce=str, validators=[Optional()])
    submit = SubmitField('Зберегти')


class EquipmentForm(FlaskForm):
    """Form for Equipment data entry"""
    name = StringField('Назва обладнання', validators=[DataRequired(), Length(min=3, max=255)])
    equipment_type = StringField('Тип обладнання', validators=[DataRequired(), Length(min=2, max=100)])
    cost = FloatField('Вартість', validators=[DataRequired()])
    purchase_date = DateField('Дата придбання', validators=[DataRequired()])
    laboratory_id = SelectField('Лабораторія', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Зберегти')


class ContractForm(FlaskForm):
    """Form for Contract data entry"""
    id = StringField('Індекс контракту', validators=[DataRequired(), Length(min=1, max=50)])
    title = StringField('Назва контракту', validators=[DataRequired(), Length(min=3, max=255)])
    start_date = DateField('Дата початку', validators=[DataRequired()])
    end_date = DateField('Дата закінчення', validators=[DataRequired()])
    budget = FloatField('Бюджет', validators=[DataRequired()])
    researcher_id = SelectField('Дослідник', validators=[DataRequired()])
    organization_id = SelectField('Організація', validators=[DataRequired()])
    submit = SubmitField('Зберегти')


# ============================================================================
# ФОРМИ ДЛЯ M-to-M ЗНОШЕНЬ (Forms for Many-to-Many Relationships)
# ============================================================================

class ExpeditionOrganizationsForm(FlaskForm):
    """Form for managing organizations financing expeditions"""
    organizations = SelectMultipleField('Організації (ФІНАНСУЄ)', coerce=str, validators=[Optional()])
    submit = SubmitField('Зберегти')


class ExpeditionEquipmentForm(FlaskForm):
    """Form for managing equipment in expeditions"""
    equipment = SelectMultipleField('Обладнання (СКЛАДАЄТЬСЯ)', coerce=int, validators=[Optional()])
    submit = SubmitField('Зберегти')


class ResearcherEquipmentForm(FlaskForm):
    """Form for managing equipment used by researchers"""
    equipment = SelectMultipleField('Обладнання (ВИКОРИСТОВУЄ)', coerce=int, validators=[Optional()])
    submit = SubmitField('Зберегти')
