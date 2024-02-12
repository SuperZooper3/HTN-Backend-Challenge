from ..models.models import Participant, BobaOrder, db

# Formatters

def format_boba_order_data(order):
    output = {}
    output[order.id] = {
        "participant_id": order.participant_id,
        "status": order.status,
        "size": order.size,
        "flavour": order.flavour,
        "sweetness": order.sweetness,
        "ice": order.ice,
        "toppings": order.toppings
    }
    return output


# Updaters

def place_boba_order(order_json):
    if "participant_id" not in order_json:
        return False, ({"error":"Participant ID required"}, 400)
    
    participant = Participant.query.get(order_json["participant_id"])
    if not participant:
        return False, ({"error":"Participant not found"}, 404)
    
    new_order = BobaOrder(participant_id=participant.id)
    if "size" in order_json:
        new_order.size = order_json["size"]
    if "flavour" in order_json:
        new_order.flavour = order_json["flavour"]
    if "sweetness" in order_json:
        new_order.sweetness = order_json["sweetness"]
    if "ice" in order_json:
        new_order.ice = order_json["ice"]
    if "toppings" in order_json:
        new_order.toppings = order_json["toppings"]

    db.session.add(new_order)
    db.session.commit()
    return True, new_order
