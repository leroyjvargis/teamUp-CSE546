from google.cloud import firestore

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

