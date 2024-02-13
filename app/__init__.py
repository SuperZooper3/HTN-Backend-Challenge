from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DATABASE_URI

# Define the databases and migrations as top level

db = SQLAlchemy()
migrate = Migrate()

# Create caching for the skills' frequency and total rating (to be used in the /skills route)
# The cache is updated by the cache helpers
skills_cache = {}

def create_app():
    global skills_cache
    # Reference the flask app based on the __name__ of the file running this function
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    # Prepare the app

    # Attach databases
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register Blueprints from the routes folder
    from .routes.participant_routes import participant_bp
    from .routes.boba_routes import boba_bp
    from .routes.skills_routes import skills_bp

    # Register all the blueprints to the app
    app.register_blueprint(participant_bp)
    app.register_blueprint(boba_bp)
    app.register_blueprint(skills_bp)

    try:
        with app.app_context():
            from .utils.cache_utils import generate_skills_cache
            skills_cache = generate_skills_cache()
            print("Skills cache generated!")
    except Exception as e:
        print(f"Error generating skills cache: {e}\n Did you initialize the database?")


    return app

def get_skills_cache():
    return skills_cache

def update_skills_cache(key, value):
    global skills_cache
    skills_cache[key] = value

