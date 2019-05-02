## TeamUp - find and match with likeminded people. 

This is the github repo for the second project in CSE 546 - ASU

### GCP setup instructions:
In a bash session, add the environment variable:
```sh
export GOOGLE_APPLICATION_CREDENTIALS="PATH_TO_CREDS_FILE"
```

The DB used is Google Firestore, setup instructions [here](https://cloud.google.com/firestore/docs/quickstart-servers)

### creds.json
Temporary JSON file for credentials storage. Will move to some other more secure method, possible environment variables. *Do not commit this file.*  
Currently following this format:
```json
{
    "googlePlacesAPIKey": "<api-key>"
}
```

### Places API types
Uses Google Places API to populate location search.  
The supported *types* or categories for the search filter are available [here](https://developers.google.com/places/supported_types)

***

### API Reference
1. /login: login user  
    method: POST  
    params: -none-  
    headers: -none-  
    returns: -none-  
    request-body: form-data  
    ```json
    {  
        "name": "string",
        "email": "string",
        "location": "string, lat-lng separated by comma"
    }
    ```


1. /home: get all events of current user  
    method: GET  
    params: -none-  
    headers: Auth: //user_email//  
    returns: list of events  
    ```json
    {  
        "category": "string",
        "created_by": {
            "name": "string",
            "email": "string"
        },
        "count_of_participants": "<number>",
        "datetime": "<datetime-object>",
        "details": "string",
        "event_id": "string",
        "max": "number",
        "min": "number",
        "name": "string",
        "status": "string"
    }  
    ```

1. /get-nearby-events: get nearby events from user location  
    method: GET  
    headers: Auth: //user_email>//  
    params:  
&nbsp;&nbsp; location_coords: string, lat-lon separated by comma  
    returns: list of events  
    ```json
    {
        "category": "string",
        "created_by": "dict, containing with email and name"
        "count_of_participants": "number",
        "datetime": "datetime-object",
        "details": "string",
        "distance": "float",
        "event_id": "string",
        "is_joined": "bool",
        "is_owner": "bool",
        "location_coords": "string",
        "location_name": "string",
        "name": "string",
        "status": "string",
    }  
    ```

1. /create-event: create an event  
    method: POST  
    headers: Auth: //user_email//  
    params: -none-  
    returns: -none-  
    request-body: form-data  
    ```json
    {  
        "name": "string",
        "details": "string",
        "location-name": "string",
        "location": "string",
        "min": "number",
        "max": "number",
        "datetime": "string, in the format M/d/Y hh:mm",
        "category": "string"
    }
    ```

1. /get-locations: get places from current location and category  
    method: GET  
    headers: -none-  
    params:  
&nbsp;&nbsp; location: coordinates as string  
&nbsp;&nbsp; category: string  
    returns: list of locations/places  
    ```json
    {  
        "address": "string",
        "distance": "float, distance in km from start location",
        "location_coords": "string, (lat,lon)",  
        "name": "string",
        "types":" list of string, containing category of location"
    }
    ```

1. /create-interest: create an interest request for current user  
    method: POST  
    headers: Auth: //user_email//  
    params: -none-  
    returns: -none-  
    request-body: form-data  
    ```json
    {  
        "category": "string",
        "location": "string",
        "radius": "string (in km)",
        "time_tag": "string (eg: sat-eve)"
    }
    ```

1. /cancel-event-participation: remove current user from an event  
    method: GET  
    headers: Auth: //user_email//  
    params:  
&nbsp;&nbsp; event_id: string  
    returns: -none-  

1. /filter-events: filter events based on some params  
    method: GET  
    headers: Auth: //user_email//  
    params: atleast one of the below are required  
&nbsp;&nbsp; event_name: string, [optional], but others are ignored if this is supplied   
&nbsp;&nbsp; vacancy: number [optional]  
&nbsp;&nbsp; distance: number (in km), requires location_coords [optional]  
&nbsp;&nbsp; location_coords: string, requried with distance [optional]  
&nbsp;&nbsp; vacancy: number [optional]  
    returns:  
    ```json
    {
        "category": "string",
        "count_of_participants": "number",
        "datetime": "datetime-object",
        "details": "string",
        "distance": "float",
        "location_coords": "string",
        "location_name": "string",
        "name": "string",
        "status": "string"
    }  
    ```

1. /add-event-user: add a user to the specified event  
    method: GET  
    headers: Auth: //user_email//  
    params:  
&nbsp;&nbsp; event_id: string  
    returns: -none-  

1. /get-categories: get all categories from system  
    method: GET  
    headers: -none-  
    params: -none-  
    returns: list of categories  

1. /delete-event: delete an event owned by user  
    method: DELETE  
    headers: Auth: //user_email//  
    params:  
&nbsp;&nbsp; event_id: string  
    returns: -none-  

1. /get-notifications: get all notifications of current user sorted by timestamp  
    method: GET  
    headers: Auth: //user_email//  
    params: -none-  
    returns:  
    ```json
    {
        "message": "string",
        "timestamp": "datetime object",
        "event": "dict of event, format as in get-nearby-events"
    }  
    ```