from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Define the databases and migrations as top level

db = SQLAlchemy()
migrate = Migrate()
