from google.cloud import firestore
import requests, datetime, json
import helpers

with open('creds.json') as json_file:  
    creds = json.load(json_file)


### BEGIN:: USER OPERATIONS ###

def loginUser(user):
    ## user -> {email: string, location: geopoint, name: string, phone: string, likes: string list}
    ## TODO: change to get details from Google SSO
    db = firestore.Client()
    location = user['location'].split(',')
    
    doc_ref = db.collection(u'users').document(user['email'])
    if (doc_ref.get().exists):
        #update location
        doc_ref.update({u'location': firestore.GeoPoint(float(location[0]), float(location[1]))})
    else:
        # create user
        doc_ref.set({
            u'email': user['email'],
            u'location': firestore.GeoPoint(float(location[0]), float(location[1])),
            u'name': user['name']
            # u'phone': user['phone'],
            # u'likes': user['likes'].split(',')
        })


def getUserEvents(user_ref):
    ## user_ref -> user-reference
    db = firestore.Client()
    #user_ref = helpers.getUserFromAuthHeader(user_ref)

    query = db.collection(u'events').where(u'is_active', u'==', True).where(u'confirmed_participants', u'array_contains', user_ref)
    query = query.stream() 
    returnData = []
    for each in query:
        ## each is an event
        data = helpers.parseEventData(each, None, "main", user_ref)
        returnData.append(data)
    return returnData


def createUserInterest(user_ref, interest):
    ## user -> user-reference
    ## interest -> {category: <string>, location: <geopoint>, radius: <number>, time-tag: <string: 'sat-morn'>, user : <user-ref>}
    db = firestore.Client()
    #user_ref = helpers.getUserFromAuthHeader(user_auth)
    location = interest['location'].split(',')

    db.collection(u'user_requests').add({
        u'category': interest['category'],
        #u'is_active': True,
        u'location': firestore.GeoPoint(float(location[0]), float(location[1])),
        u'radius': int(interest['radius']),
        u'time_tag': interest['time_tag'],
        u'event_id': "",
        u'user': user_ref
    })


def cancelUserParticipationToEvent(user_ref, eventID):
    ##TODO: handle errors
    #user_ref = helpers.getUserFromAuthHeader(user_auth)
    db = firestore.Client()

    ## find the event and remove user
    doc_ref = db.collection(u'events').document(eventID)
    event_document = doc_ref.get().to_dict()
    #event_document['confirmed_participants'].remove(user_ref) 
    event_document['confirmed_participants'] = [x.get().to_dict() for x in event_document['confirmed_participants']]
    user = user_ref.get().to_dict()
    event_document['confirmed_participants'].remove(user)
    event_document['confirmed_participants'] = [db.collection(u'users').document(x['email']) for x in event_document['confirmed_participants']]
    doc_ref.set(event_document)

    ## find the interest and update is_active
    ## find exact interest request based on eventId
    if event_document['created_by'] == 'System Bot':
        doc_ref = db.collection(u'user_requests').where(u'user', u'==', user_ref).where(u'event_id', u'==', eventID)
        document = doc_ref.stream()
        for each in document:
            each_id = each.id
            each = each.to_dict()
            each['event_id'] = ""
            db.collection(u'user_requests').document(each_id).set(each)

    addNotifications(doc_ref, "remove")
### END:: USER OPERATIONS ###



### BEGIN:: EVENT OPERATIONS ###

def createEvent(user_ref, event):
    ## event -> {name: string, details: string, location-name: location-coords: geopoint, min: number, max: number, datetime: timestamp, status: string, participants: list, category: string}
    ## TODO: datetime
    db = firestore.Client()
    #user_ref = helpers.getUserFromAuthHeader(user_ref)
    location = event['location'].split(',')

    db.collection(u'events').add({
        u'name': event['name'],
        u'category': event['category'],
        u'details': event['details'],
        u'location_name': event['location_name'],
        u'location_coords': firestore.GeoPoint(float(location[0]), float(location[1])),
        u'min': int(event['min']),
        u'max': int(event['max']),
        u'datetime': helpers.parseDateTimeFromString(event['datetime']),
        u'status': 'scheduled',
        u'is_active': True,
        u'created_by': user_ref,
        u'confirmed_participants': [user_ref]
    })


def getNearbyEvents(user, location_coords):
    ##TODO: find a better way utilizing where query in firestore rather than get all and filter
    db = firestore.Client() 
    query = db.collection(u'events')
    query = query.stream()
    location = location_coords.split(',')
    location_coords = (float(location[0]), float(location[1]))
    user_data = user.get().to_dict()

    returnData = []
    for each in query:
        data = each.to_dict()
        if 'location_coords' in data and data['is_active']:
            distance = helpers.calculateDistanceBetweenLocationCoordinates(location_coords, helpers.parseGeoPoint(data['location_coords'], 'tuple'))
            #print (each.id, distance)
            if distance < 25:
                data = helpers.parseEventData(each, location_coords, None, user_data)
                returnData.append(data)
    return returnData


def filterEvents(event_name, vacancy, distance, location_coords, category):
    ## TODO: filter based on other params
    # print("finding event name" + str(event_name))
    db = firestore.Client()
    events_ref = db.collection(u'events')

    if location_coords is not None:
        location = location_coords.split(',')
        location_coords = (float(location[0]), float(location[1]))
    returnData = []
    if event_name is not None:
        event_data = events_ref.where(u'name', u'==', event_name)
        event_data = event_data.stream()
        for each in event_data:
            returnData = helpers.parseEventData(each, location_coords)
            return returnData
            
    else:
        events_data = events_ref.stream()
        all_events = []
        for each in events_data:
            data = helpers.parseEventData(each, location_coords)
            # print(data)
            all_events.append(data)
        returnData = all_events

    # print("Testing vars ", category, " ", vacancy," " , distance)
    if category is not None and len(category)>0:
        returnData = list(filter(lambda x : str(x['category']) == str(category), returnData))

    # if vacancy is not None:
    #     returnData = list(filter(lambda x : int(x['vacancy']) >= int(vacancy) if 'vacancy' in x, returnData))
    results = []
    if vacancy is not None and len(vacancy)>0:
        for x in returnData:
            if 'vacancy' in x.keys():
                results.append(x)

        returnData = results
    
    if distance is not None and len(distance)>0:
        returnData = list(filter(lambda x : float(x['distance']) <= float(distance), returnData))
    
    # print(returnData)
    

    



        ## filter events from all_events based on the other params
        #[x for x in all_events if x['max'] - x['count_of_participants'] > vacancy]

    return returnData


def addEventUser(user_ref, event_id):
    db = firestore.Client()
    events_ref = db.collection(u'events').document(event_id)
    events_data = events_ref.get().to_dict()
    events_data['confirmed_participants'].append(user_ref)
    events_ref.update({'confirmed_participants': events_data['confirmed_participants']})
    addNotifications(events_ref)



def deleteEvent(user_ref, event_id):
    db = firestore.Client()
    events_ref = db.collection(u'events').document(event_id)
    events_data = events_ref.get().to_dict()
    created_user = helpers.parseUserFromReference(events_data['created_by'])
    current_user = helpers.parseUserFromReference(user_ref)

    if created_user['email'] == current_user['email']:
        events_ref.update({'is_active': False, 'status': 'deleted'})
    else:
        raise Exception("Unauthorized user")


def getPlacesByCategory(location, category):
    ## location -> [<lat>,<long>], category = "sports"
    ## google places API:    
    category = helpers.getGPlacesTypeForCategory(category)
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius=15000&type={}&rankBy=distance&key={}'.format(location[0], location[1], category, creds['googlePlacesAPIKey'])
    response = requests.get(url)
    data = response.json()
    return helpers.parseGooglePlacesAPIResponse(location, data)


def getNotifications(user_ref):
    db = firestore.Client()
    query = db.collection(u'notifications').where(u'is_active', u'==', True).where(u'user', u'==', user_ref)
    data = query.stream()
    returnData = []
    for each in data:
        each = each.to_dict()
        each['event'] = helpers.parseEventData(each['event'].get())
        del each['user']
        del each['is_active']
        returnData.append(each)
    returnData = sorted(returnData, key=lambda kv: kv['timestamp'], reverse=True)
    return returnData

### END:: EVENT OPERATIONS ###

def getCategories():
    categories = ['sports', 'food']
    return categories


def addNotifications(event_ref, mode="add"):
    #for each user request satisfied, create a notification
    db = firestore.Client()
    notification_ref = db.collection(u'notifications')
    event_data = event_ref.get().to_dict()

    if mode == "add":
        mode = "added to"
    else:
        mode = "removed from"
    message = 'New user {} event - {}. Total participants now at {}'.format(mode, event_data['name'], len(event_data['confirmed_participants']))
    for each_user_ref in event_data['confirmed_participants']:
        notification_ref.add({
            u'user': each_user_ref,
            u'event': event_ref,
            u'message': message,
            u'is_active': True,
            u'timestamp': datetime.datetime.now()
        })
    
