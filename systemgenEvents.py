from google.cloud import firestore
import json, requests,geopy, datetime
from geopy import distance
from geopy.distance import geodesic
import time

## DEBUG::
#with open('server/creds.json') as json_file:  
    #creds = json.load(json_file)

## PROD::
with open('creds.json') as json_file:
    creds = json.load(json_file)


days={'mon':0, 'tue':1, 'wed':2, 'thu':3, 'fri':4, 'sat':5, 'sun':6  }
time_of_day={'morn': 8, 'eve': 17}

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def getGPlacesTypeForCategory(category):
    categories = {
        'sports': 'park',
        'film': 'movie_theater',
        'food': 'restaurant'
    }
    return categories[category]

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
    categoryType = getGPlacesTypeForCategory(category)

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
            
def createSystemEvent(category, event, timetag):
    ## event = {name: string, details: string, location-name: location-coords: geopoint, min: number, max: number, datetime: timestamp, status: string, participants: map, category: string}
    db = firestore.Client()

    d=datetime.datetime.now()
    time_tag_split = timetag.split('-')
    d = datetime.datetime(d.year, d.month, d.day, time_of_day[time_tag_split[1]], 0, 0)
    next_dt = next_weekday(d, days[time_tag_split[0]])
    # print("next_dt ", next_dt)
    # eventdt = str(next_dt)[0:11]+'17'+str(next_dt)[13:19]

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
        u'datetime': next_dt,
        # u'datetime': datetime.datetime.now() + datetime.timedelta(days=3),
        u'status': 'scheduled',
        u'is_active': True,
        u'created_by': 'System Bot',
        u'confirmed_participants': event['probCandidates']
    })
    print("printing Event id " + b.id)
    for each_request_id in event['request_ids']:
        print(each_request_id)
        query= db.collection(u'user_requests').document(each_request_id).update({ u'event_id': b.id })
    
    addNotifications(event['request_ids'], b)

def addNotifications(user_request_ids, event_ref):
    #for each user request satisfied, create a notification
    db = firestore.Client()
    user_interest_ref = db.collection(u'user_requests')
    notification_ref = db.collection(u'notifications')
    event_data = event_ref.get().to_dict()
    for each in user_request_ids:
        interest_data = user_interest_ref.document(each).get().to_dict()
        user_ref = interest_data['user']
        message = 'New event created - {} on {} at {}'.format(event_data['name'], event_data['datetime'].strftime('%A, %b %d'), event_data['datetime'].strftime('%I:%M %p'))
        notification_ref.add({
            u'user': user_ref,
            u'event': event_ref,
            u'message': message,
            u'is_active': True,
            u'timestamp': datetime.datetime.now()
        })




def main():
    # timeTags = [u'mon-morn',u'mon-eve', u'tue-morn', u'tue-eve', u'wed-morn', u'wed-eve', u'thu-morn', u'thu-eve', u'fri-morn', u'fri-eve', u'sat-morn', u'sat-eve', u'sun-morn', u'sun-eve']
    categories = [u'sports' , u'food' , u'film']
    timeTags = [u'fri-morn', u'fri-eve', u'sat-morn', u'sat-eve', u'sun-morn', u'sun-eve', u'mon-morn',u'mon-eve']
    # categories = [u'sports' , u'food']


    
    for category in categories:
        for timetag in timeTags:
            ActiveRequests = getActiveRequests("", category, timetag)
            # print("ActiveRequests")
            # print(ActiveRequests)
            if len(ActiveRequests) >0:
                probableVenues = findVenues(ActiveRequests,[]) #set of probable venues
                if len(probableVenues)>0:
                    # print("length probableVenues ", len(probableVenues))
                    probableVenues = list({v['name']:v for v in probableVenues}.values())
                    # print(probableVenues)
                    # print("length probableVenues again ", len(probableVenues))
                    # print(probableVenues)
                    BestprobableVenues = findBestVenues(ActiveRequests, probableVenues)
                    BestprobableVenues = sorted(BestprobableVenues, key=lambda kv: (len(kv['probCandidates']), kv['rating']), reverse=True)
                    # print(*BestprobableVenues, sep='\n')
                    # print("BestprobableVenues")
                    print("Checking if min of attendees are available " ,len(BestprobableVenues[0]['request_ids']))
                    if len(BestprobableVenues[0]['request_ids']) >=3:
                        createSystemEvent(category,BestprobableVenues[0],timetag)

if __name__== "__main__":
    ##PROD::
    minutes_to_wait = 1
    while True: 
        print ("Processing..")
        main()
        print ("waiting for {} minutes".format(str(minutes_to_wait)))
        print ('')
        time.sleep(60*minutes_to_wait)

    ##DEBUG::
    #main()
