from flask import Blueprint, request
from ..models.models import Participant
from ..services.participant_services import *
from config import PAGE_SIZE
import time


participant_bp = Blueprint('participant_bp', __name__)


@participant_bp.route('/users', methods=['GET'])
def users():
    output = {}

    query = Participant.query

    # Apply filters
    if "checked_in" in request.args:
        checked_in_needed = request.args["checked_in"].lower() == "true"
        query = query.filter(Participant.checked_in == checked_in_needed)

    # Pagination
    if "page" in request.args:
        page = request.args["page"]
        if not page.isnumeric():
            return {"error":"Invalid page number"}, 400
        
        page = int(page)
        if page < 1:
            return {"error":"Invalid page number"}, 400
        
        query = query.offset((page-1)*PAGE_SIZE).limit(PAGE_SIZE)

    all_participants = query.all()

    for participant in all_participants:
        output.update(format_participant_data(participant))

    return output

@participant_bp.route('/users/<int:participant_id>', methods=['GET','PUT'])
def user(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    
    if request.method == "PUT":
        if (request.json):
            update_worked = update_participant(participant, request)
            if not update_worked:
                return {"error":"Invalid update"}, 400
        
    return format_participant_data(participant)

@participant_bp.route('/register', methods=['POST'])
def register():
    if not request.json:
        return {"error":"Invalid request"}, 400
    
    # Try to register the participant, get the status and response (either an error or the new participant's object)
    registration_status, registration_response = register_participant(request.json)
    if not registration_status:
        return registration_response[0], registration_response[1]
    
    new_participant = registration_response
    
    return format_participant_data(new_participant)

@participant_bp.route('/checkin', methods=['GET','POST'])
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
