from google.cloud import firestore
import geopy.distance
import requests, json



def parseUserFromReference(user, type="full"):
    ## type: full, main
    ## user: of type dict

    db = firestore.Client()
    data = user.get().to_dict()
    if type == "full":
        data['location'] = '{},{}'.format(str(data['location'].latitude), str(data['location'].longitude))
        return data
    elif type == "main":
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