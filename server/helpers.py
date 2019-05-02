from google.cloud import firestore
import geopy.distance
import requests, json, datetime



def parseUserFromReference(user, type_of_response ="full"):
    ## type_of_response: full, main
    ## user: of type dict or str (for system bot)

    if isinstance(user, str):
        return {"name": user, "email": user}
    else:
        data = user.get().to_dict()
        if type_of_response == "full":
            data['location'] = '{},{}'.format(str(data['location'].latitude), str(data['location'].longitude))
            return data
        elif type_of_response == "main":
            del data['location']
            if 'likes' in data:
                del data['likes']
            if 'phone' in data:
                del data['phone']    
        return data

def parseGooglePlacesAPIResponse(original_location, response):
    data = []
    for each in response['results']:
        original_coords = (float(original_location[0]), float(original_location[1]))
        each_coords = (each['geometry']['location']['lat'], each['geometry']['location']['lng'])
        obj = {
            'name': each['name'],
            'types': each['types'],
            #'rating': each['rating'],
            'address': each['vicinity'],
            'location_coords': '{},{}'.format(each_coords[0], each_coords[1]),
            'distance': calculateDistanceBetweenLocationCoordinates(original_coords, each_coords)
        }
        data.append(obj)
    data = sorted(data, key=lambda kv: kv['distance'])
    return data

def getGPlacesTypeForCategory(category):
    categories = {
        'sports': 'park',
        'film': 'movie_theater',
        'food': 'restaurant'
    }
    return categories[category]

def calculateDistanceBetweenLocationCoordinates(coords_1, coords_2, unit='km'):
    distance = geopy.distance.vincenty(coords_1, coords_2)
    if unit == "km":
        return distance.km
    else:
        return distance.miles

def parseGeoPoint(geopoint_location, convert_to='string'):
    if convert_to == 'string':
        return '{},{}'.format(str(geopoint_location.latitude), str(geopoint_location.longitude))
    elif convert_to == 'list':
        return [str(geopoint_location.latitude), str(geopoint_location.longitude)]
    elif convert_to == 'tuple':
        return (float(geopoint_location.latitude), float(geopoint_location.longitude))

def getUserFromAuthHeader(user):
    db = firestore.Client()
    document = db.collection(u'users').document(user)
    if document.get().exists:
        return document
    else:
        raise Exception ("Unauthorized user")

def parseEventData(event, location_coords = None, created_by = "none", user = None):
    ## event -> firestore document reference of /events/<id>
    ## user -> dict
    data = event.to_dict()
    data['event_id'] = event.id
    data['is_owner'] = False
    data['is_joined'] = False
    if location_coords is not None:
        distance = calculateDistanceBetweenLocationCoordinates(location_coords, parseGeoPoint(data['location_coords'], 'tuple'))
        data['distance'] = distance
    if user is not None:
        participants = [x.get().to_dict()['email'] for x in data['confirmed_participants']]
        if user['email'] in participants:
            data['is_joined'] = True
    data['count_of_participants'] = len(data['confirmed_participants'])
    del data['confirmed_participants']

    if 'max' in data:
        data['vacancy'] = data['max'] - data['count_of_participants'] if data['max'] - data['count_of_participants'] > 0 else 0

    data['location_coords'] = parseGeoPoint(data['location_coords'])
    if created_by is not "none":
        data['created_by'] = parseUserFromReference(data['created_by'], 'main')
        if user is not None and data['created_by']['email'] == user['email']:
            data['is_owner'] = True
    else:
        del data['created_by']
    del data['is_active']
    return data

def parseDateTimeFromString(datetime_string):
    ## datetime_string: m/d/Y hh:mm 
    datetime_string = datetime_string.split(' ')
    date_part = datetime_string[0]
    time_part = datetime_string[1]
    date_part = date_part.split('/')
    time_part = time_part.split(':')
    return datetime.datetime(int(date_part[2]), int(date_part[0]), int(date_part[1]), int(time_part[0]), int(time_part[1]), 0)