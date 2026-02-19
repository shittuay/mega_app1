# CLAUDE.md — AI Assistant Guide for mega_app1

## Project Overview

**mega_app1** is a multi-module Flask web application ("Mega App") that provides several productivity and lifestyle tools in a single codebase. It uses the Flask Application Factory pattern with Blueprints to organize each feature as a self-contained module.

### Feature Modules

| Module | URL Prefix | Description |
|---|---|---|
| Budget Tracker | `/budget` | Manage income and expense transactions |
| Habit Tracker | `/habit` | Track daily habits with per-day completion records |
| Task Manager | `/task` | Create and manage tasks with due dates |
| Fitness Tracker | `/fitness` | Log workouts with title, description, and duration |
| Mood Journal | `/mood` | Record daily mood entries |
| Coding Journal | `/coding` | Log coding progress notes and journal entries |
| Community Board | `/community` | Post and browse community messages |
| Motivational Quotes | `/motivational` | Save and display motivational quotes |
| Weather App | `/weather` | Fetch live weather data via OpenWeatherMap API |

---

## Repository Structure

```
mega_app1/
├── run.py                    # Top-level entry point: creates and runs the Flask app
├── config.py                 # Root Config class (SECRET_KEY, DATABASE_URL, SQLAlchemy settings)
├── requirements.txt          # Root-level Python dependencies
├── README.md
├── app/
│   ├── __init__.py           # Application factory (create_app), DB/migrate/login init, blueprint registration
│   ├── models.py             # All SQLAlchemy ORM models
│   ├── forms.py              # All WTForms form classes
│   ├── budget.py             # Budget blueprint (routes)
│   ├── habit.py              # Habit blueprint (routes)
│   ├── fitness.py            # Fitness blueprint (routes)
│   ├── mood.py               # Mood blueprint (routes)
│   ├── coding.py             # Coding journal blueprint (routes)
│   ├── community.py          # Community board blueprint (routes)
│   ├── motivational.py       # Motivational quotes blueprint (routes)
│   ├── weather.py            # Weather blueprint (routes + OpenWeatherMap API call)
│   ├── templates/
│   │   ├── base.html         # Base Jinja2 template (currently empty — needs content)
│   │   ├── budget/           # budget index + add_transaction templates
│   │   ├── coding/           # coding index, add_entry, coding_detail templates
│   │   ├── community/        # community index, add_post, community_detail templates
│   │   ├── fitness/          # fitness index, add_workout, workout_detail templates
│   │   ├── habit/            # habit index, add_habit, habit_detail templates
│   │   ├── mood/             # mood index, add_mood, mood_detail templates
│   │   ├── motivational/     # motivational index, add_quote templates
│   │   ├── task/             # task index, add_task, task_detail templates
│   │   └── weather/          # weather index template
│   ├── migrations/
│   │   ├── config.py         # Duplicate Config class (same as root config.py)
│   │   └── .env              # Empty env file placeholder
│   ├── requirements.txt      # Duplicate/alternate requirements (slightly different versions)
│   ├── run.py                # Duplicate entry point inside app/ (use the root run.py)
│   └── venv/                 # Inner virtual environment (use the root venv/ instead)
├── venv/                     # Primary virtual environment
└── __pycache__/
```

---

## Known Issues and Tech Debt

> These issues exist in the current codebase. Be aware of them when making changes.

1. **`task.py` is missing**: `app/__init__.py` imports and registers `task_bp` from `app.task`, but `app/task.py` does not exist. The app will fail to start until this file is created.

2. **Duplicate model definitions in `models.py`**: Both `Workout` and `Habit` (and `HabitRecord`) are defined twice in `app/models.py`. The second definition silently shadows the first. Python will use the last definition. Deduplicate before adding new models.

3. **`base.html` is empty**: `app/templates/base.html` contains no content. All templates that extend it will render blank pages until this is populated.

4. **Weather API key is hardcoded as a placeholder**: `app/weather.py` contains `API_KEY = 'your_openweathermap_api_key'`. This must be replaced with a real key (preferably via environment variable) for the weather module to work.

5. **Duplicate files**: `app/run.py`, `app/requirements.txt`, `app/migrations/config.py`, and `app/venv/` are duplicates of root-level files. Always use the root-level versions.

6. **No Flask-Login user model**: `Flask-Login` is initialized in `__init__.py` and listed in requirements, but no `User` model, `@login_manager.user_loader`, or authentication routes exist.

7. **`db.create_all()` + `flask db init/migrate/upgrade` on every start**: The `create_app()` factory runs these commands inside `with app.app_context()` on startup if the migrations directory doesn't exist. This can fail or produce unexpected behavior in production.

---

## Database Models

All models are in `app/models.py` and use SQLAlchemy via `flask_sqlalchemy`.

| Model | Table | Key Fields |
|---|---|---|
| `BudgetTransaction` | `budget_transaction` | `title`, `amount`, `type` (income/expense), `date` |
| `Habit` | `habit` | `name`, `description`, `creation_date`; has `records` relationship |
| `HabitRecord` | `habit_record` | `date`, `status` (bool), `habit_id` (FK to `habit.id`) |
| `Task` | `task` | `title`, `description`, `due_date`, `completed` (bool) |
| `Workout` | `workout` | `title`, `description`, `date`, `duration` (minutes) |
| `Mood` | `mood` | `title`, `description`, `date` |
| `CodingEntry` | `coding_entry` | `title`, `content`, `date_posted` |
| `CommunityPost` | `community_post` | `title`, `author`, `content`, `date_posted` |
| `MotivationalQuote` | `motivational_quote` | `content`, `author`, `date_posted` |

---

## Forms

All WTForms are defined in `app/forms.py` using `flask_wtf.FlaskForm`.

| Form Class | Used By |
|---|---|
| `BudgetTransactionForm` | budget blueprint |
| `HabitForm` | habit blueprint |
| `HabitRecordForm` | habit blueprint (detail view) |
| `TaskForm` | task blueprint |
| `TaskUpdateForm` | task blueprint (edit view) |
| `WorkoutForm` | fitness blueprint |
| `MoodForm` | mood blueprint |
| `CodingEntryForm` | coding blueprint |
| `CommunityPostForm` | community blueprint |
| `MotivationalQuoteForm` | motivational blueprint |
| `WeatherForm` | weather blueprint |

---

## Configuration

Configuration is handled by the `Config` class in the root `config.py`.

| Setting | Default | Override Via |
|---|---|---|
| `SECRET_KEY` | `'you-will-never-guess'` | `SECRET_KEY` env var |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///app.db` (in project root) | `DATABASE_URL` env var |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | N/A |

Create a `.env` file in the project root to override defaults:

```
SECRET_KEY=your-secure-secret-key
DATABASE_URL=sqlite:///app.db
```

---

## Development Setup

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone and enter the project
cd mega_app1

# Create and activate virtual environment (use root-level venv only)
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate.bat       # Windows CMD
venv\Scripts\Activate.ps1       # Windows PowerShell

# Install dependencies (use root requirements.txt)
pip install -r requirements.txt
```

### Running the Application

```bash
python run.py
```

The app runs at `http://127.0.0.1:5000` in debug mode.

### Database Migrations

If not using the auto-init in `create_app()`:

```bash
flask db init
flask db migrate -m "Description of changes"
flask db upgrade
```

---

## Blueprint Architecture Pattern

Each feature module follows this consistent pattern:

```python
# app/<module>.py
from flask import Blueprint, render_template, url_for, flash, redirect
from app import db
from app.models import ModelClass
from app.forms import FormClass

<module>_bp = Blueprint('<module>', __name__)

@<module>_bp.route('/')
def index():
    items = ModelClass.query.order_by(ModelClass.date.desc()).all()
    return render_template('<module>/index.html', items=items)

@<module>_bp.route('/add', methods=['GET', 'POST'])
def add_<item>():
    form = FormClass()
    if form.validate_on_submit():
        item = ModelClass(title=form.title.data, ...)
        db.session.add(item)
        db.session.commit()
        flash('Item added!', 'success')
        return redirect(url_for('<module>.index'))
    return render_template('<module>/add_<item>.html', form=form)
```

### Adding a New Module

1. Create `app/<module>.py` with a Blueprint named `<module>_bp`
2. Add the model class to `app/models.py`
3. Add the form class to `app/forms.py`
4. Create template directory `app/templates/<module>/` with `index.html` and relevant sub-templates
5. Register the blueprint in `app/__init__.py`:
   ```python
   from app.<module> import <module>_bp
   app.register_blueprint(<module>_bp, url_prefix='/<module>')
   ```
6. Run `flask db migrate -m "Add <module> model"` and `flask db upgrade`

---

## Template Conventions

- Templates live in `app/templates/<module>/`
- All templates should extend `base.html`: `{% extends 'base.html' %}`
- Flash messages use Bootstrap alert categories: `'success'`, `'danger'`, `'warning'`, `'info'`
- Forms are rendered with WTForms and must include the CSRF token: `{{ form.hidden_tag() }}`

---

## Dependencies

Core packages (from root `requirements.txt`):

| Package | Version | Purpose |
|---|---|---|
| Flask | 1.1.4 | Web framework |
| Flask-SQLAlchemy | 2.4.4 | ORM integration |
| SQLAlchemy | 1.3.23 | ORM |
| Flask-Migrate | 2.5.3 | Database migrations (Alembic wrapper) |
| Flask-WTF | 0.14.3 | Form handling + CSRF protection |
| Flask-Login | 0.5.0 | User session management (not yet implemented) |
| requests | 2.26.0 | HTTP client (used by weather module) |
| python-dotenv | 0.15.0 | Load `.env` files |
| markupsafe | 2.0.1 | Safe HTML markup (Jinja2 dependency) |

---

## Testing

There are currently no tests in this repository. When adding tests:

- Use `pytest` as the test runner
- Create a `tests/` directory at the project root
- Use Flask's test client: `app.test_client()`
- Use an in-memory SQLite database for tests: `SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'`

---

## Security Notes

- `SECRET_KEY` defaults to a hardcoded value — always override in production via environment variable
- The Weather module's `API_KEY` is hardcoded — move to environment variable before deploying
- No authentication is implemented despite Flask-Login being installed
- CSRF protection is active via Flask-WTF (requires `SECRET_KEY` to be set)
