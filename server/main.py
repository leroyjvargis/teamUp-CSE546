from flask import Flask, request, jsonify, abort
import engine, helpers, systemgenEvents

app = Flask(__name__)


@app.route('/')
def root():
    message = "All your base are belong to us!"
    return jsonify({'message': message})

@app.route('/login', methods=['POST'])
def register():
    if not request or not request.form:
        abort(400)
    engine.loginUser(request.form)
    return jsonify(success=True), 201

@app.route('/home', methods=['GET'])
def home():
    if not request:
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)
    events = engine.getUserEvents(user)
    return jsonify(events), 200

@app.route('/get-nearby-events', methods=['GET'])
def get_nearby_events():
    if not request or not request.args.get('location_coords'):
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)
    events = engine.getNearbyEvents(user, request.args.get('location_coords'))
    return jsonify(events), 200

@app.route('/create-event', methods=['POST'])
def create_event():
    if not request or not request.form:
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)
    engine.createEvent(user, request.form)
    return jsonify(success=True), 201

@app.route('/get-locations', methods=['GET'])
def get_locations():
    if not request or not request.args.get('location') or not request.args.get('category'):
        abort(400)
    location = request.args.get('location').split(',')
    category = request.args.get('category')
    data = engine.getPlacesByCategory(location, category)
    return jsonify(data), 200

@app.route('/filter-events', methods=['GET'])
def filter_events():
    if not request:
        abort(400)
    if request.args.get('distance') and not request.args.get('location'):
        abort (400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)

    location = request.args.get('location')
    event_name = request.args.get('event_name')
    vacancy = request.args.get('vacancy')
    distance = request.args.get('distance')
    category = request.args.get('category')
    data = engine.filterEvents(event_name, vacancy, distance, location, category)
    return jsonify(data), 200

@app.route('/create-interest', methods=['POST'])
def create_interest():
    if not request or not request.form:
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)
    engine.createUserInterest(user, request.form)
    return jsonify(success=True), 201

@app.route('/get-interests', methods=['GET'])
def get_interst():
    if not request:
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)
    data = engine.getUserInterests(user)
    return jsonify(data), 200

@app.route('/delete-interest', methods=['DELETE'])
def delete_interest():
    if not request or not request.args.get('interest_id'):
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)
    engine.deleteUserInterest(user, request.args.get('interest_id'))
    return jsonify(success=True), 200


@app.route('/cancel-event-participation', methods=['GET'])
def cancel_event_participation():
    if not request or not request.args.get('event_id'):
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)
    engine.cancelUserParticipationToEvent(user, request.args.get('event_id'))
    return jsonify(success=True), 200

@app.route('/get-categories', methods=['GET'])
def get_categories():
    return jsonify(engine.getCategories())

@app.route('/add-event-user', methods=['GET'])
def add_event_user():
    if not request or not request.args.get('event_id'):
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)
    engine.addEventUser(user, request.args.get('event_id'))
    return jsonify(success=True), 200

@app.route('/delete-event', methods=['DELETE'])
def delete_event():
    if not request or not request.args.get('event_id'):
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
        engine.deleteEvent(user, request.args.get('event_id'))
    except:
        abort(401)
    return jsonify(success=True), 200

@app.route('/get-notifications', methods=['GET'])
def get_notifications():
    if not request:
        abort(400)
    if not request.headers.get('Auth'):
        abort(401)
    try:
        ## checking auth here
        user = helpers.getUserFromAuthHeader(request.headers.get('Auth'))
    except:
        abort(401)
    data = engine.getNotifications(user)
    return jsonify(data), 200

@app.route('/run-task', methods=['POST'])
def run_tasks():
    systemgenEvents.main()
    return jsonify(success=True), 200


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
