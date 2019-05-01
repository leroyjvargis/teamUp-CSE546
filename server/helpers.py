from google.cloud import firestore
import geopy.distance
import requests, json



def parseUserFromReference(user, type_of_response ="full"):
    ## type_of_response: full, main
    ## user: of type dict

    if isinstance(user, str):
        return {"name": user, "email": user}
    else:
        data = user.get().to_dict()
        if type_of_response == "full":
            data['location'] = '{},{}'.format(str(data['location'].latitude), str(data['location'].longitude))
            return data
        elif type_of_response == "main":
            del data['location']
            del data['likes']
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
            'distance': calculateDistanceBetweenLocationCoordinates(original_coords, each_coords)
        }
        data.append(obj)
    data = sorted(data, key=lambda kv: kv['distance'])
    return data

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

def parseEventData(event, location_coords = None, created_by = "none"):
    ## event -> firestore document reference of /events/<id>
    data = event.to_dict()
    print (data)
    if location_coords is not None:
        distance = calculateDistanceBetweenLocationCoordinates(location_coords, parseGeoPoint(data['location_coords'], 'tuple'))
        data['distance'] = distance
    data['count_of_participants'] = len(data['confirmed_participants'])
    if 'max' in data:
        data['vacancy'] = data['max'] - data['count_of_participants'] if data['max'] - data['count_of_participants'] > 0 else 0
    data['location_coords'] = parseGeoPoint(data['location_coords'])
    del data['confirmed_participants']
    if created_by is not "none":
        data['created_by'] = parseUserFromReference(data['created_by'], created_by)
    else:
        del data['created_by']
    return data