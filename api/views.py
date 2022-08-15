from api import app, db
from flask import request, jsonify
from api.models import Screen, Row


@app.before_first_request
def create_tables():
    db.create_all()

    
@app.route('/')
def greet():
    return 'Hey you..Welcome!'


# Route for entering the details of various screens one at a time
'''
{
    "name": "inox",
    "seatInfo": {
        "A": {
            "numberOfSeats": 10
        },
        "B": {
            "numberOfSeats": 15
        },
        "C": {
            "numberOfSeats": 20
        }
    }
}
'''
@app.route('/screens', methods=['POST'])
def screens():
    try:
        name = request.json['name']
        seat_info = request.json['seatInfo']
    except:
        return jsonify({"status": 400, "message": "Bad Request"})

    try:
        screen = Screen(name=name)
        db.session.add(screen)
        db.session.commit()

        screen = Screen.query.filter_by(name=name).first()

        for key, value in seat_info.items():
            num_seats = value['numberOfSeats']
            row_id = str(screen.id) + '_' + key # Eg: 1_A ;  id is a unique id made of "screen_id + row_alphabet"
            row = Row(id=row_id,
                      number_of_seats=num_seats,
                      reserved_seats="")
            db.session.add(row)
            db.session.commit()

        return jsonify({"status": 200, "message": "Screen details successfully added"})
    except :
        return jsonify({"status": 400,
                        "message": "Failure to add screen details.This may occur due to duplicate entry of screen name"})
