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
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String)
    skills = db.relationship("Skills", backref="participant")
    checked_in = db.Column(db.Boolean, default=False)
    check_in_id = db.Column(db.Integer, db.ForeignKey('check_in.id'))

class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    rating = db.Column(db.Integer)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))

class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.relationship("Participant", backref="check_in")
    time = db.Column(db.Integer)
    volunteer_id = db.Column(db.Integer)


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

def new_participant_skill_to_cache(skill, rating):
    """Updates the skills cache with a new skill, or updates the frequency and total rating of an existing skill. For when it's a participant's first time adding a skill. Not for when they update their rating."""
    if skill not in skills_cache:
        skills_cache[skill] = {
            "frequency": 1,
            "total_rating": rating
        }
    else:
        skills_cache[skill]["frequency"] += 1
        skills_cache[skill]["total_rating"] += rating

# Query functions
def format_participant_data(participant):
    output = {}
    if participant:
        output[participant.id] = {
            "name": participant.name,
            "company": participant.company,
            "email": participant.email,
            "phone": participant.phone,
            "checked_in": participant.checked_in,
            "skills": []
        }
        for skill in participant.skills:
            output[participant.id]["skills"].append({
                "skill": skill.name,
                "rating": skill.rating
            })
    return output

def format_checkin_data(participant):
    output = {}
    output["participant_id"] = participant.id
    output["checked_in"] = participant.checked_in
    if participant.checked_in:
        if not participant.check_in_id:
            return {"error":"Participant has checked in but has no check-in ID"}, 500
        
        checkin = CheckIn.query.get_or_404(participant.check_in_id)
        output["check_in_time"] = checkin.time
        output["volunteer_id"] = checkin.volunteer_id
    return output

# Update functions
def register_participant(participant_json):
    # Check all fields are present
    mandatory_fields = ["name","company","email","phone"]
    for field in mandatory_fields:
        if field not in participant_json:
            return False, ({"error":f"{field} required"}, 400)
        
    # Check for if the email is already in use
    if Participant.query.filter_by(email=participant_json["email"]).first():
        return False, ({"error":"Email Already Exists"}, 400)

    new_participant = Participant(name=participant_json["name"], company=participant_json["company"], email=participant_json["email"], phone=participant_json["phone"])
    db.session.add(new_participant)
    # # Commit the changes to generate the participant ID
    db.session.commit()
    for skill in participant_json["skills"]:
        if "rating" not in skill or type(skill["rating"]) != int or skill["rating"] < 1 or skill["rating"] > 5:
            return {"error":"Invalid rating"}, 400
        
        new_skill = Skills(name=skill["skill"], rating=skill["rating"], participant_id=new_participant.id)
        db.session.add(new_skill)
        new_participant_skill_to_cache(skill["skill"], skill["rating"])

    db.session.commit()
    return True, new_participant

def update_participant(participant, request):
    simple_updatable_fields = ["name","company","email","phone"]
    for field in simple_updatable_fields:
        if field in request.json:
            if field == "email":
                user_with_same_email = Participant.query.filter_by(email=request.json["email"]).first()
                if user_with_same_email and user_with_same_email.id != participant.id:
                    return False
            
            participant.__setattr__(field,request.json[field])
    
    if "skills" in request.json:
        participants_skills = {skill.name:skill for skill in participant.skills}
        for skill in request.json["skills"]:
            if "rating" not in skill or type(skill["rating"]) != int or skill["rating"] < 1 or skill["rating"] > 5:
                return False
            
            if skill["skill"] not in participants_skills:
                new_skill = Skills(name=skill["skill"], rating=skill["rating"], participant_id=participant.id)
                db.session.add(new_skill)
                participants_skills[skill["skill"]] = new_skill

                # Update the skills cache
                new_participant_skill_to_cache(skill["skill"], skill["rating"])
            else:
                old_rating = participants_skills[skill["skill"]].rating
                participants_skills[skill["skill"]].rating = skill["rating"]

                # Update the skills cache for an updated change instead of a new addition
                skills_cache[skill["skill"]]["total_rating"] += skill["rating"] - old_rating
    
    db.session.commit()
    return True


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
        output.update(format_participant_data(participant))

    return output

@app.route('/users/<int:participant_id>', methods=['GET','PUT'])
def user(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    
    if request.method == "PUT":
        if (request.json):
            update_worked = update_participant(participant, request)
            if not update_worked:
                return {"error":"Invalid update"}, 400
        
    return format_participant_data(participant)

@app.route('/register', methods=['POST'])
def register():
    if not request.json:
        return {"error":"Invalid request"}, 400
    
    # Try to register the participant, get the status and response (either an error or the new participant's object)
    registration_status, registration_response = register_participant(request.json)
    if not registration_status:
        return registration_response[0], registration_response[1]
    
    new_participant = registration_response
    
    return format_participant_data(new_participant)

@app.route('/skills', methods=['GET'])
def skills():
    output = {}
    min_frequency = request.args.get("min_frequency", None, type=int)
    max_frequency = request.args.get("max_frequency", None, type=int)
    min_average_rating = request.args.get("min_average_rating", None, type=float)
    max_average_rating = request.args.get("max_average_rating", None, type=float)
    keyword = request.args.get("keyword", None, type=str)

    for skill in skills_cache:
        if check_skill_frequency(skill, min_frequency, max_frequency) and check_skill_average_rating(skill, min_average_rating, max_average_rating) and (keyword is None or keyword.lower() in skill.lower()):
            output[skill] = {
                "frequency": skills_cache[skill]["frequency"],
                "average_rating": round(skills_cache[skill]["total_rating"] / skills_cache[skill]["frequency"], 2)
            }
    return output

@app.route('/checkin', methods=['GET','POST'])
def checkin():
    if request.method == "GET":
        if "participant_id" not in request.args:
            return {"error":"Participant ID required"}, 400
        participant = Participant.query.get_or_404(request.args["participant_id"])
        return format_checkin_data(participant)

    elif request.method == "POST":
        if not request.json or "participant_id" not in request.json:
            return {"error":"Participant ID required"}, 400

        if "volunteer_id" not in request.json:
            return {"error":"Volunteer ID required"}, 400

        participant = Participant.query.get_or_404(request.json["participant_id"])
        if participant.checked_in:
            return {"error":"Already checked in"}, 400
        
        new_checkin = CheckIn(time=int(time.time()), volunteer_id=request.json["volunteer_id"])
        db.session.add(new_checkin)

        # Commit the changes to generate the check-in ID
        db.session.commit()

        participant.checked_in = True
        participant.check_in_id = new_checkin.id

        db.session.commit()
        return format_checkin_data(participant)
    
    return {"error":"Invalid request"}, 400

# Run the app

if __name__ == "__main__":
    try:
        with app.app_context():
            skills_cache = generate_skills_cache()
            print("Skills cache generated!")
    except Exception as e:
        print(f"Error generating skills cache: {e}\n Did you initialize the database?")
    
    app.run(port=8000,debug=True)

