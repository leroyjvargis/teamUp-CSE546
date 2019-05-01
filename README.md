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
1. /home: get all events of current user:  
    method: GET  
    params: -none-  
    headers: Auth: <user_email>  
    returns: list of events  
&nbsp;  {  
&nbsp;&nbsp;&nbsp;&nbsp; category: string,  
&nbsp;&nbsp;&nbsp;&nbsp; created_by: {  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; name: string,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; email: string  
&nbsp;&nbsp;&nbsp;&nbsp; },  
&nbsp;&nbsp;&nbsp;&nbsp; count_of_participants: number,  
&nbsp;&nbsp;&nbsp;&nbsp; datetime: datetime-object,  
&nbsp;&nbsp;&nbsp;&nbsp; details: string,  
&nbsp;&nbsp;&nbsp;&nbsp; event_id: string,  
&nbsp;&nbsp;&nbsp;&nbsp; max: number,  
&nbsp;&nbsp;&nbsp;&nbsp; min: number,  
&nbsp;&nbsp;&nbsp;&nbsp; name: string,  
&nbsp;&nbsp;&nbsp;&nbsp; status: string  
&nbsp; }  

1. /get-nearby-events: get nearby events from user location:  
    method: GET  
    headers: -none-  
    params:  
&nbsp;&nbsp; location_coords: string, lat-lon separated by comma  
    returns: list of events  
&nbsp;        {  
&nbsp;&nbsp;&nbsp;&nbsp; category: string,  
&nbsp;&nbsp;&nbsp;&nbsp; count_of_participants: number,  
&nbsp;&nbsp;&nbsp;&nbsp; datetime: datetime-object,  
&nbsp;&nbsp;&nbsp;&nbsp; details: string,  
&nbsp;&nbsp;&nbsp;&nbsp; distance: float,  
&nbsp;&nbsp;&nbsp;&nbsp; location_coords: string,  
&nbsp;&nbsp;&nbsp;&nbsp; location_name: string,  
&nbsp;&nbsp;&nbsp;&nbsp; name: string,  
&nbsp;&nbsp;&nbsp;&nbsp; status: string  
&nbsp; }  

1. /create-event: create an event  
    method: POST  
    headers: Auth: //user_email//  
    params: -none-  
    returns: -none-
    request-body: form-data  
&nbsp;        {
&nbsp;&nbsp;&nbsp;&nbsp; name: string,  
&nbsp;&nbsp;&nbsp;&nbsp; details: string,  
&nbsp;&nbsp;&nbsp;&nbsp; location-name: string,  
&nbsp;&nbsp;&nbsp;&nbsp; location: string,  
&nbsp;&nbsp;&nbsp;&nbsp; min: number,  
&nbsp;&nbsp;&nbsp;&nbsp; max: number,  
&nbsp;&nbsp;&nbsp;&nbsp; datetime: string,  
&nbsp;&nbsp;&nbsp;&nbsp; category: string,  
&nbsp; }

1. /get-locations: get places from current location and category  
    method: GET  
    headers: -none-  
    params:  
&nbsp;&nbsp; location: coordinates as string  
&nbsp;&nbsp; category: string  
    returns: list of locations/places  
&nbsp;          {  
&nbsp;&nbsp;&nbsp;&nbsp; address: string,  
&nbsp;&nbsp;&nbsp;&nbsp; distance: float, distance in km from start location,  
&nbsp;&nbsp;&nbsp;&nbsp; name: string,  
&nbsp;&nbsp;&nbsp;&nbsp; types: list of string, containing category of location  
&nbsp; }

1. /create-interest: create an interest request  
    method: POST  
    headers: Auth: //user_email//  
    params: -none-  
    returns: -none-  
    request-body: form-data  
&nbsp;        {
&nbsp;&nbsp;&nbsp;&nbsp; category: string,  
&nbsp;&nbsp;&nbsp;&nbsp; location: string,  
&nbsp;&nbsp;&nbsp;&nbsp; radius: string (in km),  
&nbsp;&nbsp;&nbsp;&nbsp; time_tag: string (eg: sat-eve)  
&nbsp; }

1. /cancel-event-participation: remove current user from an event  
    method: GET  
    headers: Auth: //user_email//  
    params:  
&nbsp;&nbsp; event_id: string  
    returns: -none-  