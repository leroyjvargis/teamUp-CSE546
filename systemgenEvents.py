from google.cloud import firestore
import json, requests,geopy, datetime
from geopy import distance
from geopy.distance import geodesic

with open('server/creds.json') as json_file:  
    creds = json.load(json_file)

def getPlacesByCategory(location, category,radii):
    ## location = [<lat>,<long>], category = "sports" , radii = 100* radius(conversion to meters but its not perfect conversion)
    ## google places API:    
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius={}&types={}&key={}'.format(location[0], location[1], radii, category, creds['googlePlacesAPIKey'])
    response = requests.get(url)
    data = response.json()
    # print(data['results'][0])
    return parseGooglePlacesAPIResponse(location, data)


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

def getActiveRequests(event_id, category, timetag):
    ## user = user-email, from header-value
    ## TODO: change header to 
    db = firestore.Client()
    categoryType = "stadium"

    query = db.collection(u'user_requests').where(u'event_id', u'==' , event_id).where(u'category', u'==' , category).where(u'time_tag', u'==' , timetag)
    query = query.stream()
    returnData = []
    for each in query:
        ## each is an event
        request_id = each.id
        data = each.to_dict()
        nearby=[]
        if 'location' in data:
            data['location'] = '{},{}'.format(str(data['location'].latitude), str(data['location'].longitude))
            data['request_id'] = request_id
            locationPoints = data['location'].split(',')
            # print(locationPoints)
            nearby = getPlacesByCategory(locationPoints, categoryType, 1000*int(data['radius']))
            data['nearby'] = nearby

        returnData.append(data)
        
    return returnData
    
def findVenues(ActiveRequests, probableVenues):
    for eachrequest in ActiveRequests:
        nearbyObj = eachrequest['nearby']
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
    # add set code for probableVenues
    for eachplacedict in probableVenues:
        eachplacedict['probCandidates'] = list()
        eachplacedict['request_ids'] = list()
        for eachrequest in ActiveRequests:
            if(geopy.distance.geodesic(eachrequest['location'],  eachplacedict['found_loc_coords']).km <= eachrequest['radius']):
                eachplacedict['probCandidates'].append(eachrequest['user'])
                eachplacedict['request_ids'].append(eachrequest['request_id'])
    return probableVenues
            
def createSystemEvent(category, event):
    ## event = {name: string, details: string, location-name: location-coords: geopoint, min: number, max: number, datetime: timestamp, status: string, participants: map, category: string}
    db = firestore.Client()
    # user_ref = db.collection(u'users').document(user)
    # location = event['location'].split(',')

    # doc_ref = db.collection(u'events').document(category+ " @ " +event['name'])
    a,b = db.collection(u'events').add({
        u'name': category + " @ " + event['name'],
        u'location_name': event['name'],
        u'category': category,
        u'details': "Address : " + event['address'],
        u'location_coords': firestore.GeoPoint(float(event['found_loc_coords'][0]), float(event['found_loc_coords'][1])),
        # u'min': int(event['min']),
        # u'max': int(event['max']),
        u'datetime': datetime.datetime.now() + datetime.timedelta(days=3),
        u'status': 'scheduled',
        u'created_by': 'System Bot',
        u'confirmed_participants': event['probCandidates']
    })
    print("printing id " + b.id)
    for each_request_id in event['request_ids']:
        print(each_request_id)
        q= db.collection(u'user_requests').document(each_request_id).update({ u'event_id': b.id })
        # q=q.stream()
        # print(q)
        # for each in q:
        #     print(each.to_dict())
        # # .set({ u'event_id': b.id })
        


def main():
    # timeTag = [u'Mon_mo',u'Mon_ev', u'Tues_mo', u'Tues_ev', u'Wed_mo', u'Wed_ev', u'Thurs_mo', u'Thurs_ev', u'Fri_mo', u'Fri_ev', u'Fri_nite', u'Sat_mo', u'Sat_ev', u'Sat_nite', u'Sun_mo', u'Sun_ev']
    timeTag2 = [u'sun-morn', u'fri-eve']
    category = u'sports'

    for timetag in timeTag2:
        ActiveRequests = getActiveRequests("", category, timetag)
        if len(ActiveRequests) >0:
            probableVenues = findVenues(ActiveRequests,[]) #set of probable venues
            # print(probableVenues)
            BestprobableVenues = findBestVenues(ActiveRequests, probableVenues)
            BestprobableVenues = sorted(BestprobableVenues, key=lambda kv: (len(kv['probCandidates']), kv['rating']), reverse=True)
            # print(*BestprobableVenues, sep='\n')
            createSystemEvent('sports',BestprobableVenues[2])

if __name__== "__main__":
    main()
