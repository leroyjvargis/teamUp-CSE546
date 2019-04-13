from google.cloud import firestore
import requests, datetime


def registerUser(user):
    ## user = {email: string, location: geopoint, name: string, phone: string, likes: string list}
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

def createEvent(user, event):
    ## event = {name: string, details: string, location-name: location-coords: geopoint, min: number, max: number, datetime: timestamp, status: string, participants: map, category: string}
    db = firestore.Client()
    user_ref = db.collection(u'users').document(user)
    location = event['location'].split(',')

    doc_ref = db.collection(u'events').document(event['category']+event['name'])
    doc_ref.set({
        u'name': event['name'],
        u'category': event['category'],
        u'details': event['details'],
        u'location-name': event['location-name'],
        u'location-coords': firestore.GeoPoint(float(location[0]), float(location[1])),
        u'min': int(event['min']),
        u'max': int(event['max']),
        u'datetime': datetime.datetime.now(),
        u'status': 'scheduled',
        u'created_by': user_ref,
        u'participants': [{
                'is_confimed': True,
                'user': user_ref
        }]
    })
