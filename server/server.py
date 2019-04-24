from flask import Flask, request, jsonify, abort
import engine

app = Flask(__name__)


@app.route('/')
def root():
    message = "All your base are belong to us!"
    return jsonify({'message': message})

@app.route('/register', methods=['POST'])
def register():
    if not request or not request.form:
        abort(400)
    engine.registerUser(request.form)
    return jsonify(success=True, status_code=200)

@app.route('/home', methods=['GET'])
def home():
    if not request or not request.headers.get('user'):
        abort(500)
    events = engine.getUserEvents(request.headers.get('user'))
    return jsonify(events)

@app.route('/create-event', methods=['POST'])
def create_event():
    if not request or not request.form:
        abort(400)
    engine.createEvent(request.headers.get('user'), request.form)
    return jsonify(success=True, status_code=200)

@app.route('/get-locations', methods=['GET'])
def get_locations():
    if not request or not request.form:
        abort(400)
    location = request.args.get('location').split(',')
    category = request.args.get('category')
    data = engine.getPlacesByCategory(location, category)
    return jsonify(data)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.2', port=8080, debug=True)
