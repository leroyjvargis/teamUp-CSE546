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
            'distance': geopy.distance.vincenty(original_coords, each_coords).km
        }
        data.append(obj)
    data = sorted(data, key=lambda kv: kv['distance'])
    return data

def parseGeoPoint(geopoint_location, convert_to='string',):
    if convert_to == 'string':
        return '{},{}'.format(str(geopoint_location.latitude), str(geopoint_location.longitude))
    elif convert_to == 'list':
        return [str(geopoint_location.latitude), str(geopoint_location.longitude)]

def getUserFromAuthHeader(user):
    db = firestore.Client()
    return db.collection(u'users').document(user)