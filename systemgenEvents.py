from google.cloud import firestore
import json, requests,geopy, datetime
from geopy import distance
from geopy.distance import geodesic

with open('server/creds.json') as json_file:  
    creds = json.load(json_file)

def getPlacesByCategory(location, category,radii):
    ## location = [<lat>,<long>], category = "sports" , radii = 100* radius(conversion to meters but its not perfect conversion)
    ## google places API:    
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius={}&key={}'.format(location[0], location[1], radii, creds['googlePlacesAPIKey'])
    response = requests.get(url)
    data = response.json()
    # print(data['results'][0])
    return parseGooglePlacesAPIResponse(location, data)[:5]


def parseGooglePlacesAPIResponse(original_location, response):
    data = []
    for each in response['results']:
        original_coords = (float(original_location[0]), float(original_location[1]))
        each_coords = (each['geometry']['location']['lat'], each['geometry']['location']['lng'])
        obj = {
            'place_coords':each_coords,
            'name': each['name'],
            'types': each['types'],
            'rating': each['rating'] if 'rating' in each else 2.5,
            'address': each['vicinity'],
            'distance': geopy.distance.geodesic(original_coords, each_coords).km
        }
        data.append(obj)
    data = sorted(data, key=lambda kv: kv['distance'])
    return data    

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

def getActiveRequests(timetag, category, eventCreated, status=True):
    ## user = user-email, from header-value
    ## TODO: change header to 
    db = firestore.Client()

    query = db.collection(u'user_requests').where(u'is_active', u'==' , status).where(u'event_created', u'==' , eventCreated).where(u'category', u'==' ,category).where(u'time_tag', u'==' ,timetag)
    query = query.stream()
    returnData = []
    for each in query:
        ## each is an event
        data = each.to_dict()
        nearby=[]
        if 'location' in data:
            data['location'] = '{},{}'.format(str(data['location'].latitude), str(data['location'].longitude))
            locationPoints = data['location'].split(',')
            # print(locationPoints)
            nearby = getPlacesByCategory(locationPoints, data['category'], 100*int(data['radius']))
            data['nearby'] = nearby

        returnData.append(data)
        
    return returnData
    
def findVenues(ActiveRequests, probableVenues):
    for perrequest in ActiveRequests:
        nearbyObj = perrequest['nearby']
        for eachplace in nearbyObj:
            obj = {
            'found_loc_coords': eachplace['place_coords'],
            'name': eachplace['name'],
            'rating': eachplace['rating'],
            'address': eachplace['address']
        }
            probableVenues.append(obj)
        return probableVenues

def findBestVenues(ActiveRequests, probableVenues):
    for eachplacedict in probableVenues:
        eachplacedict['probCandidates'] = list()
        for perrequest in ActiveRequests:
            if(geopy.distance.geodesic(perrequest['location'],  eachplacedict['found_loc_coords']).km <= perrequest['radius'] ):
                eachplacedict['probCandidates'].append(perrequest['user'])
    return probableVenues
            
def createSystemEvent(category, event):
    ## event = {name: string, details: string, location-name: location-coords: geopoint, min: number, max: number, datetime: timestamp, status: string, participants: map, category: string}
    db = firestore.Client()
    # user_ref = db.collection(u'users').document(user)
    # location = event['location'].split(',')

    doc_ref = db.collection(u'events').document(category+ " @ " +event['name'])
    doc_ref.set({
        u'name': category + " @ " + event['name'],
        u'location-name': event['name'],
        u'category': category,
        u'details': "Address : " + event['address'],
        u'location-coords': firestore.GeoPoint(float(event['found_loc_coords'][0]), float(event['found_loc_coords'][1])),
        # u'min': int(event['min']),
        # u'max': int(event['max']),
        u'datetime': datetime.datetime.now() + datetime.timedelta(days=4),
        u'status': 'scheduled',
        u'created_by': 'System Bot',
        u'confirmed_participants': event['probCandidates']
    })


def main():
    # timeTag = [u'Mon_mo',u'Mon_ev', u'Tues_mo', u'Tues_ev', u'Wed_mo', u'Wed_ev', u'Thurs_mo', u'Thurs_ev', u'Fri_mo', u'Fri_ev', u'Fri_nite', u'Sat_mo', u'Sat_ev', u'Sat_nite', u'Sun_mo', u'Sun_ev']
    timeTag2 = [u'sat-noon', u'Sun_ev']
    category = u'sports'

    for timetag in timeTag2:
        ActiveRequests = getActiveRequests(timetag,category, False, True)
        if len(ActiveRequests) >0:
            probableVenues = findVenues(ActiveRequests,[])
            # print(probableVenues)
            BestprobableVenues = findBestVenues(ActiveRequests, probableVenues)
            BestprobableVenues = sorted(BestprobableVenues, key=lambda kv: (len(kv['probCandidates']), kv['rating']), reverse=True)
            print(*BestprobableVenues, sep='\n')
            createSystemEvent('Soccer',BestprobableVenues[0])

if __name__== "__main__":
    main()
