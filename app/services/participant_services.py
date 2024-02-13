from ..models.models import Participant, CheckIn, Skills, db
from ..utils.cache_utils import new_participant_skill_to_cache, get_skills_cache, update_skills_cache

# Formatters to json-ify participants

def format_participant_data(participant):
    output = {}
    if participant:
        output[participant.id] = {
            "name": participant.name,
            "company": participant.company,
            "email": participant.email,
            "phone": participant.phone,
            "checked_in": participant.checked_in,
            "bbt_tokens": participant.bbt_tokens,
            "bbt_tokens_last_exchange_time": participant.bbt_tokens_last_exchange_time,
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


# Updaters

# Register a new participant
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


# Update a participant's information
def update_participant(participant, request):
    # To configure the fields that can be updated, add them to this list. For example bubble tea tokens and checked_in are not updatable by the user simply
    simple_updatable_fields = ["name","company","email","phone"]
    # Iterate through the fields that can be updated, instead of over the fields given in the request
    for field in simple_updatable_fields:
        if field in request.json:
            if field == "email":
                user_with_same_email = Participant.query.filter_by(email=request.json["email"]).first()
                if user_with_same_email and user_with_same_email.id != participant.id:
                    return False
            
            participant.__setattr__(field,request.json[field])
    
    # Update the skills
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
                update_skills_cache(skill["skill"],{
                    "frequency": get_skills_cache()[skill["skill"]]["frequency"],
                    "total_rating": get_skills_cache()[skill["skill"]]["total_rating"] + skill["rating"] - old_rating
                })
    
    db.session.commit()
    return True

# Give a participant bubble tea tokens. Returns a tuple of (success, new token count)
def give_bbt_tokens(participant, tokens):
    try:
        participant.bbt_tokens += tokens
        db.session.commit()
        return True, participant.bbt_tokens
    except:
        return False, -1
