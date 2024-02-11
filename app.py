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


# Simple query methods
def get_participant_data(participant):
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
                    else:
                        participants_skills[skill["skill"]].rating = skill["rating"]
            
            db.session.commit()
        
    return get_participant_data(participant)


if __name__ == "__main__":
    app.run(port=8000,debug=True)

