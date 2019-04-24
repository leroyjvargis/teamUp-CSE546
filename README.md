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
