from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Define the databases and migrations as top level

db = SQLAlchemy()
migrate = Migrate()

# Create caching for the skills' frequency and total rating (to be used in the /skills route)
# The cache is updated by the cache helpers
skills_cache = {}

