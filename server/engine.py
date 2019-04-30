from google.cloud import firestore
import requests, datetime, json
import helpers

with open('creds.json') as json_file:  
    creds = json.load(json_file)


### BEGIN:: USER OPERATIONS ###

def registerUser(user):
    ## user -> {email: string, location: geopoint, name: string, phone: string, likes: string list}
    ## TODO: change to get details from Google SSO
    db = firestore.Client()
    location = user['location'].split(',')
    
    doc_ref = db.collection(u'users').document(user['email'])
    doc_ref.set({
        u'email': user['email'],
        u'location': firestore.GeoPoint(float(location[0]), float(location[1])),
        u'name': user['name'],
        u'phone': user['phone'],
        u'likes': user['likes'].split(',')
    })

def getUserEvents(user_auth):
    ## user -> user-email, from header-value
    ## TODO: change header to proper auth
    db = firestore.Client()
    user_ref = helpers.getUserFromAuthHeader(user_auth)

    query = db.collection(u'events').where(u'confirmed_participants', u'array_contains', user_ref)
    query = query.stream() 
    returnData = []
    for each in query:
        ## each is an event
        data = each.to_dict()
        data['created_by'] = helpers.parseUserFromReference(data['created_by'], "main") #.get().to_dict()
        if 'location_coords' in data:
            data['location_coords'] = helpers.parseGeoPoint(data['location_coords'])
        del data['confirmed_participants']
        returnData.append(data)
    return returnData


def createUserInterest(user_auth, interest):
    ## TODO: auth user
    ## user -> user-email
    ## interest -> {category: <string>, location: <geopoint>, radius: <number>, time-tag: <string: 'sat-morn'>, user : <user-ref>}
    db = firestore.Client()
    user_ref = helpers.getUserFromAuthHeader(user_auth)
    location = interest['location'].split(',')

    db.collection(u'user_requests').add({
        u'category': interest['category'],
        u'is_active': True,
        u'location': firestore.GeoPoint(float(location[0]), float(location[1])),
        u'radius': int(interest['radius']),
        u'time_tag': interest['time_tag'],
        u'user': user_ref
    })

def cancelUserParticipationToEvent(user)
    s = 1
### END:: USER OPERATIONS ###



### BEGIN:: EVENT OPERATIONS ###

def createEvent(user_auth, event):
    ## event -> {name: string, details: string, location-name: location-coords: geopoint, min: number, max: number, datetime: timestamp, status: string, participants: list, category: string}
    ## TODO: datetime
    db = firestore.Client()
    user_ref = helpers.getUserFromAuthHeader(user_auth)
    location = event['location'].split(',')

    db.collection(u'events').add({
        u'name': event['name'],
        u'category': event['category'],
        u'details': event['details'],
        u'location_name': event['location_name'],
        u'location_coords': firestore.GeoPoint(float(location[0]), float(location[1])),
        u'min': int(event['min']),
        u'max': int(event['max']),
        u'datetime': datetime.datetime.now(),
        u'status': 'scheduled',
        u'created_by': user_ref,
        u'confirmed_participants': [user_ref]
    })


def getPlacesByCategory(location, category):
    ## location -> [<lat>,<long>], category = "sports"
    ## google places API:    
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius=1500&type={}&key={}'.format(location[0], location[1], category, creds['googlePlacesAPIKey'])
    response = requests.get(url)
    data = response.json()
    return helpers.parseGooglePlacesAPIResponse(location, data)[:5]

### END:: EVENT OPERATIONS ###


#print (getPlacesByCategory(['33.4197241', '-111.9305695'], 'park'))