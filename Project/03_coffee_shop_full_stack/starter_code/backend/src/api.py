import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import db
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    # Get all the drinks from db
    drinks = Drink.query.all()

    drinks_data = []
    for drink in drinks:
        drinks_data.append(drink.short())

    return {
        'success': True,
        'drinks': drinks_data
    }, 200
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    # Get all the drinks from db
    drinks = Drink.query.all()

    drinks_data = [drink.long() for drink in drinks]

    return {
        'success': True,
        'drinks': drinks_data
    }, 200
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    # Get the body
    req = request.get_json()

    try:
        # Create a new Drink object
        drink = Drink(
            title=req.get('title'),
            recipe=json.dumps(req.get('recipe'))
        )

        # Insert the new Drink into the database
        db.session.add(drink)
        db.session.commit()

    except Exception:
        db.session.rollback()
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    # Get the body
    req = request.get_json()

    # Get the Drink with requested Id
    drink = Drink.query.get(id)

    # If no drink with the given id, abort
    if drink is None:
        abort(404)

    try:
        # Update the drink attributes if they exist in the request body
        if 'title' in req:
            drink.title = req['title']
        if 'recipe' in req:
            drink.recipe = json.dumps(req['recipe'])

        # Commit the changes to the database
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # Get the Drink with requested Id
    drink = Drink.query.get(id)

    # If no drink with the given id, abort
    if drink is None:
        abort(404)

    try:
        # Delete the drink
        db.session.delete(drink)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(400)

    return jsonify({'success': True, 'delete': id}), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
def create_error_response(message, error_code):
    response = jsonify({
        'success': False,
        'error': error_code,
        'message': message
    })
    response.status_code = error_code
    return response


@app.errorhandler(Exception)
def handle_exception(error):
    status_code = 500
    if isinstance(error, HTTPException):
        status_code = error.code
    return create_error_response(str(error), status_code)


@app.errorhandler(AuthError)
def handle_auth_error(error):
    return create_error_response(error.error['description'], error.status_code)


@app.errorhandler(404)
def handle_not_found_error(error):
    return create_error_response('Resource not found', 404)


@app.errorhandler(401)
def handle_unauthorized_error(error):
    return create_error_response('Unauthorized', 401)


@app.errorhandler(400)
def handle_bad_request_error(error):
    return create_error_response('Bad Request', 400)


@app.errorhandler(405)
def handle_method_not_allowed_error(error):
    return create_error_response('Method Not Allowed', 405)


if __name__ == '__main__':
    app.run(debug=True)
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
