from google.cloud import firestore
import requests


def registerUser(user):
    ## user = {email: string, location: geostorage, name: string, phone: string, preferences: string list}
    db = firestore.Client()
    location = user['location'].split(',')
    
    doc_ref = db.collection(u'users').document(user['email'])
    doc_ref.set({
        u'email': user['email'],
        u'location': firestore.GeoPoint(float(location[0]), float(location[1])),
        u'name': user['name'],
        u'phone': user['phone'],
        u'preferences': user['preferences'].split(',')
    })