from app import app, db, migrate, Participant, Skills
import json

INPUT_NAME = "HTN_2023_BE_Challenge_Data.json"

def full_reset_database():
    # Clear the old database
    db.drop_all()
    db.create_all()

    # Load in the data from the JSON file
    with open(INPUT_NAME, "r") as f:
        data = json.load(f)

    for participant in data:
        new_participant = Participant(name=participant["name"], company=participant["company"], email=participant["email"], phone=participant["phone"])
        db.session.add(new_participant)
        # # Commit the changes to generate the participant ID
        db.session.commit()
        for skill in participant["skills"]:
            new_skill = Skills(name=skill["skill"], rating=skill["rating"], participant_id=new_participant.id)
            db.session.add(new_skill)

    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        full_reset_database()
        
    print(f"Database reset with data from {INPUT_NAME}!")