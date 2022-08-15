# Movie Ticket Booking API

The developed API has the following functionalities:
- Add details of a screen (rows and number of seats in each row).
- Get the seats available in each row for a particular screen.
- Reserve one or multiple available seats

**Assumptions**
1. By screen, we mean a single cinema hall.  
eg: INOX_Delhi is a screen while INOX_Kanpur is another screen. 
2. For the sake of simplicity, we assume that only one show is scheduled on a single day.
3. Our cinema hall has rows with continuous seats, no break in between. Hence no aisle seats, except for the ones at each end.  
This is what our movie theatre looks like:  
![movie_theatre](https://user-images.githubusercontent.com/15028913/184633930-5781d05d-ca06-4e15-ae27-c6f762aa61e8.jpg)

## Creating our Development Environment

Our repo structure:
```
movie-ticket-booking-api  
├── api  
├── requirements.txt  
├── README.md  
├── .venv
├── run.py  
```

- **movie-ticket-booking-api** is our root directory and contains all the project related code, configuration and environment. It contains two sub-directories **api** and **.venv**.
- **api** directory contains all the source code related to our API.
- **.venv**  is the virtual environment for the project.
- The **run.py** file is the main file which is executed first whenever the application is started.
- **README.md** is what you're reading.
- **requirements.txt** contains all the dependencies of the project.

It's a good practice to create a virtual environment for our project rather than using the global environment.

### Create the virtual environment
```
$ python3 -m venv .venv
```

### Activate the virtual environment
```
$ source .venv/bin/activate
```

### Install flask using pip3
```
$ pip3 install flask
```

### Install flask_sqlalchemy using pip3
```
$ pip3 install flask_sqlalchemy
```

## Developing the API

The contents of the **run.py** file are as follows:
```
from api import app
```

We nee to initialize our app and databases. To do this change into **api** directory and create three files:
- \__init\__.py  - Initialises our app and databases
- models.py - contains the classes/models for our database
- routes.py - contains the endpoints of our API.

The contents of the **\__init\__.py** file are as follows:
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///ticketing.db'

db = SQLAlchemy(app)

from api import views

if __name__ == '__main__':
    app.run(debug=True)
```

Create the database models in the 'models.py' file
```python
from api import db

# DB model for relation (id, screen_name). One-to-One mapping of unique ids with screen_name
class Screen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

# DB model for relation (id, number_of_seats, reserved_seats)
# This relation stores the details of each row of a screen.
# id is a unique id made of "screen_id + row_alphabet"
class Row(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    number_of_seats = db.Column(db.Integer)
    reserved_seats = db.Column(db.String())
```

### Defining the endpoints of our API

Our API will have three endpoints:
1. **/screens**  - Add new screen and screen details. This endpoint will use the HTTP **POST** method to add a new screen using data in JSON format in the request body.
2. **/screens/<screen_name>/seats** - Get information about unreserved seats in each row. This endpoint uses the HTTP **GET** method.
3. **/screens/<screen_name>/reserve** - Reserve seats at a given screen identified by screen_name. The details of the seats to be reserved are provided in the request body in JSON format. This endpoint also uses the HTTP **POST** method.

**GET** and **POST** are HTTP methods. HTTP defines a set of request methods to indicate the desired action to be performed for a given resource.
- **GET** : The GET method requests a representation of the specified resource. Requests using GET should ***only retrieve data***.
- **POST** : The POST method is used to ***submit an entity to the specified resource***, often causing a change in state on the server (eg: change in the database, etc.)

## Adding a new screen : /screens 

The purpose of this endpoint is to add a new screen and its details. Since we would be hosting our API on localhost, the URL for this endpoint would be: http://127.0.0.1:5000//screens  

The name of the screen and the data about the number of seats will be sent in JSON format in the request body.  
An example would look like:
```json
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
```
The above JSON object contains data about 'inox'. There are three rows A, B and C with 10, 15 and 20 seats respectively.

To handle this request add the following code in **views.py** file
```python
from api import app, db
from flask import request, jsonify
from api.models import Screen, Row

@app.before_first_request
def create_tables():
    db.create_all()

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
```

Now that we have our 1st end-point we can test it on Postman.  
<img width="1392" alt="add_screen_details" src="https://user-images.githubusercontent.com/15028913/184635836-0ae5b87e-8b90-4270-965f-7f87ace378cd.png">

After sending the request we receive a success message(bottom pane) indicating that our '/screens' API end-point works well.

----
## Reserving seats at a screen: /screens/<screen_name>/reserve

This end-point uses POST method as the reserved seats have to be marked in the database thus changing the state of the server. The request body contains the information of the seats to be reserved in JSON format.  
Here is the URL for this endpoint: http://127.0.0.1:5000//screens/<screen_name>/reserve

An example of the request body sent in JSON format to reserve seats would look like:
```json
{
    "seats" : {
        "A": [1,2],
        "B": [10,11],
        "C": [6,7]
    }
}
```

To handle this request add the following code to **views.py** file.
```python
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
        reserved_seats = "_".join(str(x) for x in reserved_seats) #list to string with '_' between each element
        row.reserved_seats = reserved_seats # updated string of reserved seats
        db.session.commit()

    return jsonify({"status": 200, "message": "Seats successfully reserved"})
```

Testing it on Postman  
<img width="1392" alt="reserve_seats" src="https://user-images.githubusercontent.com/15028913/184636968-391f4193-2981-4780-b489-8fa6ff136f0c.png">

## Viewing information of unreserved seats - /screens/<screen_name>/seats 

This end-point uses GET method to retrieve data about all the unreserved seats at a screen. The parameter used is 'status' with possible value as 'unreserved'.

The URL for this endpoint would look like: http://127.0.0.1:5000//screens/inox/seats?status=unreserved  
Here, '?' denotes the start of URL parameters, after which numerous parameters can exist in the form of key-value pairs separated by '&'. Our endpoint uses just one parameter.

To handle this request add the following code to **views.py** file.
```python
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
    rows = Row.query.filter(Row.id.like("%"+str(id)+"%")).all() # All rows of inox : "1_A", "1_B", "1_C"
    result = dict()
    seats = dict()
    for row in rows:
        reserved = row.reserved_seats.split('_') # list of reserved seat nos(in string format) for each row
        num = row.number_of_seats # total seats for each row
        lst = list(range(0, num))
        for item in reserved:
            try:
                lst.remove(int(item))
            except:
                None
        seats[row.id[-1]] = lst # If our id was "1_A", then row.id[-1] will give us 'A'. Proceeds lly for all rows
    result["seats"] = seats
    
    # Return a list of all unreserved seats
    return jsonify(result)
```

Now that we have the code to handle the request to this endpoint, let's test it.  
<img width="1392" alt="show_unreserved_seats" src="https://user-images.githubusercontent.com/15028913/184638026-ea0502ce-797b-408b-a869-016805c807b1.png">

Finally, we have all the code we need to make this simple API to add screen details, book tickets and see available seats.
