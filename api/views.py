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

    
# Route for reserving a ticket at a given screen
# Example of a request URL : 'http://localhost:8080/screens/inox/reserve
'''
{
    "seats" : {
        "A" : [1,2],
        "B" : [10,11],
        "C" : [6,7]
    }
}
'''
@app.route('/screens/<screen_name>/reserve', methods=['POST'])
def reserve_seats(screen_name):
    if not screen_name:
        return jsonify({"message": "Bad request", "status": 400})
    screen = Screen.query.filter_by(name=screen_name).first()
    seats = request.json['seats']
    
    # Check whether the required seats are available or not
    for key, value in seats.items():
        req_seats = value
        row_id = str(screen.id) + '_' + key
        row = Row.query.filter_by(id=row_id).first()
        reserved_seats = row.reserved_seats.split('_')
        for seat_no in req_seats:
            if str(seat_no) in reserved_seats:
                return jsonify({"status": 400,
                                "message": "Cannot reserve specified seats!"})

    # Mark the reserved seats in the database
    for key, value in seats.items():
        row_id = str(screen.id) + '_' + key
        row = Row.query.filter_by(id=row_id).first() #1_A
        reserved_seats = row.reserved_seats.split('_') # list of reserved seat numbers(type:string)
        reserved_seats += value # as the requested seats are available, add then as well to reserved
        reserved_seats = "_".join(str(x) for x in reserved_seats) #list to string with _ between each element
        row.reserved_seats = reserved_seats # updated string of reserved seats
        db.session.commit()

    return jsonify({"status": 200, "message": "Seats successfully reserved"})

    
# Route to get available seats(all unreserved seats) for a given screen.
# Eg. 'http://localhost:8080/screens/inox/seats?status=unreserved'
@app.route('/screens/<screen_name>/seats', methods=['GET'])
def available_seats(screen_name):
    status = None
    try:
        status = request.args.get('status')
    except:
        pass
    if status != "unreserved":
        return jsonify({"message": "Bad request", "status": 400})

    # Get the screen object from database with name=screen_name
    screen = Screen.query.filter_by(name=screen_name).first()
    id = screen.id
    # Get all the rows at the screen given by 'screen_name'
    rows = Row.query.filter(Row.id.like("%"+str(id)+"%")).all()
    result = dict()
    seats = dict()
    for row in rows:
        reserved = row.reserved_seats.split('_') #list of reserved seat nos(in string format) for each row
        num = row.number_of_seats # total seats for each row
        lst = list(range(0, num))
        for item in reserved:
            try:
                lst.remove(int(item))
            except:
                None
        seats[row.id[-1]] = lst
    result["seats"] = seats
    
    # Return a list of all unreserved seats
    return jsonify(result)
