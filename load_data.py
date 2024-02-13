from app import create_app, db
from app.services.participant_services import register_participant
import json

INPUT_NAME = "HTN_2023_BE_Challenge_Data.json"

def full_reset_database():
    # Create the app 
    app = create_app()

    with app.app_context():
        # Clear the old database
        db.drop_all()
        db.create_all()

        # Load in the data from the JSON file
        with open(INPUT_NAME, "r") as f:
            data = json.load(f)

        for participant in data:
            register_participant(participant)

        db.session.commit()

if __name__ == "__main__":
    full_reset_database()
    print(f"Database reset with data from {INPUT_NAME}!")