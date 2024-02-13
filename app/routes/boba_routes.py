from flask import Blueprint, request
from ..models.models import BobaOrder
from ..services.participant_services import give_bbt_tokens
from ..services.boba_services import *
from config import BOBA_STATUSES, BBT_TOKENS_COOLDOWN, BBT_TOKENS_PER_ORDER
import time


boba_bp = Blueprint('boba_bp', __name__)

@boba_bp.route('/boba', methods=['GET','POST','PUT'])
def boba():
    if request.method == "GET":
        query = BobaOrder.query

        if "participant_id" in request.args:
            if not request.args["participant_id"].isnumeric():
                return {"error":"Invalid participant ID"}, 400
            participant_id = int(request.args["participant_id"])
            query = query.filter(BobaOrder.participant_id == participant_id)

        if "status" in request.args:
            status = request.args["status"]
            query = query.filter(BobaOrder.status == status)

        all_orders = query.all()

        output = {}
        for order in all_orders:
            output.update(format_boba_order_data(order))

        return output

    elif request.method == "POST":
        if not request.json or "participant_id" not in request.json:
            return {"error":"Participant ID required"}, 400
        
        participant = Participant.query.get(request.json["participant_id"])
        if not participant:
            return {"error":"Participant not found"}, 404
        
        if participant.bbt_tokens < BBT_TOKENS_PER_ORDER:
            return {"error":"Not enough tokens to order"}, 400
        
        placed_status, placed_order = place_boba_order(request.json)
        if not placed_status:
            return placed_order[0], placed_order[1]
        else:
            # If the order was placed successfully, deduct the tokens from the participant
            participant.bbt_tokens -= BBT_TOKENS_PER_ORDER
            db.session.commit()
            return format_boba_order_data(placed_order)

    elif request.method == "PUT":
        if not request.json or "order_id" not in request.json:
            return {"error":"Order ID required"}, 400
        
        order = BobaOrder.query.filter_by(id=request.json["order_id"]).first()
        if not order:
            return {"error":"Order not found"}, 404
        
        if "status" in request.json and request.json["status"] in BOBA_STATUSES:
            order.status = request.json["status"]
        else:
            return {"error":"Invalid status"}, 400
        
        db.session.commit()
        return format_boba_order_data(order)

    else:
        return {"error":"Invalid request"}, 400
    
@boba_bp.route('/boba_info', methods=['GET'])
def boba_info():
    return {
        "boba_statuses": BOBA_STATUSES,
        "boba_tokens_per_order": BBT_TOKENS_PER_ORDER,
        "boba_tokens_cooldown": BBT_TOKENS_COOLDOWN
    }
    
@boba_bp.route('/bbt_token_exchange', methods=['PUT'])
def bbt_token_exchange():
    if not request.json:
        return {"error":"Invalid request, needs json"}, 400
    
    if "participant_1_id" not in request.json:
        return {"error":"participant_1_id required"}, 400
    if "participant_2_id" not in request.json:
        return {"error":"participant_2_id required"}, 400
    
    if request.json["participant_1_id"] == request.json["participant_2_id"]:
        return {"error":"Cannot exchange tokens with yourself"}, 400
    
    participant_1 = Participant.query.get_or_404(request.json["participant_1_id"])
    participant_2 = Participant.query.get_or_404(request.json["participant_2_id"])

    if time.time() - participant_1.bbt_tokens_last_exchange_time < BBT_TOKENS_COOLDOWN:
        return {"error":"Participant 1 has not waited long enough to exchange tokens"}, 400
    
    if time.time() - participant_2.bbt_tokens_last_exchange_time < BBT_TOKENS_COOLDOWN:
        return {"error":"Participant 2 has not waited long enough to exchange tokens"}, 400

    give_bbt_tokens(participant_1,tokens=1)
    give_bbt_tokens(participant_2,tokens=1)

    participant_1.bbt_tokens_last_exchange_time = int(time.time())
    participant_2.bbt_tokens_last_exchange_time = int(time.time())
    db.session.commit()

    return {"success":"Tokens exchanged", "new_tokens_1":participant_1.bbt_tokens, "new_tokens_2":participant_2.bbt_tokens}, 200

@boba_bp.route('/bbt_token_admin_give', methods=['PUT'])
def bbt_token_admin_give():
    if not request.json:
        return {"error":"Invalid request, needs json"}, 400
    
    if "participant_id" not in request.json:
        return {"error":"participant_id required"}, 400
    if "tokens" not in request.json:
        return {"error":"tokens required"}, 400
    
    participant = Participant.query.get_or_404(request.json["participant_id"])
    give_bbt_tokens(participant,tokens=request.json["tokens"])
    return {"success":"Tokens given", "new_tokens":participant.bbt_tokens}, 200
