from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import os
import time
DATABASE_NAME = "htn.db"

# Create the Flask app and connect it to the SQLite database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'
db = SQLAlchemy(app)

# Create a migration object to generate the database with `flask db init`, `flask db migrate`, and `flask db upgrade
migrate = Migrate(app, db)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    company = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    skills = db.relationship("Skills", backref="participant")

class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    rating = db.Column(db.Integer)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))


# Create caching for the skills' frequency and total rating (to be used in the /skills route)
skills_cache = {}

def generate_skills_cache():
    fresh_cache = {}
    all_skills = Skills.query.all()
    for skill in all_skills:
        if skill.name not in fresh_cache:
            fresh_cache[skill.name] = {
                "frequency": 0,
                "total_rating": 0
            }
        fresh_cache[skill.name]["frequency"] += 1
        fresh_cache[skill.name]["total_rating"] += skill.rating

    return fresh_cache

# Query functions
def format_participant_data(participant):
    output = {}
    if participant:
        output[participant.id] = {
            "name": participant.name,
            "company": participant.company,
            "email": participant.email,
            "phone": participant.phone,
            "skills": []
        }
        for skill in participant.skills:
            output[participant.id]["skills"].append({
                "skill": skill.name,
                "rating": skill.rating
            })
    return output

# Update functions
def update_participant(participant, request):
    simple_updatable_fields = ["name","company","email","phone"]
    for field in simple_updatable_fields:
        if field in request.json:
            participant.__setattr__(field,request.json[field])
    
    if "skills" in request.json:
        participants_skills = {skill.name:skill for skill in participant.skills}
        for skill in request.json["skills"]:
            if type(skill["rating"]) != int or skill["rating"] < 1 or skill["rating"] > 5:
                return {"error":"Invalid rating"}, 400
            
            if skill["skill"] not in participants_skills:
                new_skill = Skills(name=skill["skill"], rating=skill["rating"], participant_id=participant.id)
                db.session.add(new_skill)
                participants_skills[skill["skill"]] = new_skill

                # Update the skills cache
                if skill["skill"] not in skills_cache:
                    skills_cache[skill["skill"]] = {
                        "frequency": 1,
                        "total_rating": skill["rating"]
                    }
                else:
                    skills_cache[skill["skill"]]["frequency"] += 1
                    skills_cache[skill["skill"]]["total_rating"] += skill["rating"]
            else:
                old_rating = participants_skills[skill["skill"]].rating
                participants_skills[skill["skill"]].rating = skill["rating"]

                # Update the skills cache for an updated change instead of a new addition
                skills_cache[skill["skill"]]["total_rating"] += skill["rating"] - old_rating
    
    db.session.commit()


# Helper methods for checks
def check_skill_frequency(skill, min_frequency, max_frequency):
    frequency = skills_cache[skill]["frequency"]
    return (min_frequency is None or frequency >= min_frequency) and (max_frequency is None or frequency <= max_frequency)

def check_skill_average_rating(skill, min_average_rating, max_average_rating):
    average_rating = skills_cache[skill]["total_rating"] / skills_cache[skill]["frequency"]
    return (min_average_rating is None or average_rating >= min_average_rating) and (max_average_rating is None or average_rating <= max_average_rating)

# Routes

@app.route('/users', methods=['GET'])
def users():
    output = {}
    all_participants = Participant.query.all()
    for participant in all_participants:
        output[participant.id] = {
            "name": participant.name,
            "company": participant.company,
            "email": participant.email,
            "phone": participant.phone,
            "skills": []
        }
        for skill in participant.skills:
            output[participant.id]["skills"].append({
                "skill": skill.name,
                "rating": skill.rating
            })

    return output

@app.route('/users/<int:participant_id>', methods=['GET','PUT'])
def user(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    
    if request.method == "PUT":
        if (request.json):
            update_participant(participant, request)
        
    return format_participant_data(participant)

@app.route('/skills', methods=['GET'])
def skills():
    output = {}
    min_frequency = request.args.get("min_frequency", None, type=int)
    max_frequency = request.args.get("max_frequency", None, type=int)
    min_average_rating = request.args.get("min_average_rating", None, type=float)
    max_average_rating = request.args.get("max_average_rating", None, type=float)

    for skill in skills_cache:
        if check_skill_frequency(skill, min_frequency, max_frequency) and check_skill_average_rating(skill, min_average_rating, max_average_rating):
            output[skill] = {
                "frequency": skills_cache[skill]["frequency"],
                "average_rating": round(skills_cache[skill]["total_rating"] / skills_cache[skill]["frequency"], 2)
            }
    return output

# Run the app

if __name__ == "__main__":
    with app.app_context():
        skills_cache = generate_skills_cache()
        print("Skills cache generated!")
    
    app.run(port=8000,debug=True)

