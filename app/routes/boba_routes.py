from flask import Blueprint, request
from ..models.models import BobaOrder
from ..services.boba_services import *
from config import BOBA_STATUSES


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
        
        placed_status, placed_order = place_boba_order(request.json)
        if not placed_status:
            return placed_order[0], placed_order[1]
        else:
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
