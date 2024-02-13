from .. import db

# Add all the models to the app's database

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    company = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String)
    skills = db.relationship("Skills", backref="participant")
    boba_orders = db.relationship("BobaOrder", backref="participant")
    bbt_tokens = db.Column(db.Integer, default=0)
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

class BobaOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    status = db.Column(db.String, default="Placed")
    size = db.Column(db.String, default="Medium")
    flavour = db.Column(db.String, default="HK Milk Tea")
    sweetness = db.Column(db.String, default="50% Sweet")
    ice = db.Column(db.String, default="Regular Ice")
    toppings = db.Column(db.String, default="None")
