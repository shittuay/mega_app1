from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate, init, migrate as migrate_command, upgrade
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return None

    # Register blueprints
    from app.budget import budget_bp
    from app.habit import habit_bp
    from app.task import task_bp
    from app.fitness import fitness_bp
    from app.mood import mood_bp
    from app.coding import coding_bp
    from app.community import community_bp
    from app.motivational import motivational_bp
    from app.weather import weather_bp

    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(habit_bp, url_prefix='/habit')
    app.register_blueprint(task_bp, url_prefix='/task')
    app.register_blueprint(fitness_bp, url_prefix='/fitness')
    app.register_blueprint(mood_bp, url_prefix='/mood')
    app.register_blueprint(coding_bp, url_prefix='/coding')
    app.register_blueprint(community_bp, url_prefix='/community')
    app.register_blueprint(motivational_bp, url_prefix='/motivational')
    app.register_blueprint(weather_bp, url_prefix='/weather')

    from app.ai_assistant import ai_bp
    app.register_blueprint(ai_bp, url_prefix='/ai')

    # Initialize the database
    with app.app_context():
        if not os.path.exists(os.path.join(app.root_path, 'migrations')):
            db.create_all()
            from flask_migrate import init, migrate, upgrade
            init()
            migrate(message='Initial migration')
            upgrade()

    return app
