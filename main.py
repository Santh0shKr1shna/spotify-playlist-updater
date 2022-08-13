
import base64
import datetime
import json
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
from scrapper import Scrapper
import requests

load_dotenv()

url = "https://accounts.spotify.com/api/token"

client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
user_id = os.getenv('user_id')

class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
            # return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']  # seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')

    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')

    def base_search(self, query_params):  # type
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        r = r.json()

        with open("./test.json","w") as file:
            json.dump(r,file)

        print(r)
        return r

    def search(self, query=None, operator=None, operator_query=None, search_type='artist', limit=1):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        print(query_params)
        return self.base_search(query_params+f"&limit={limit}")

    def create_playlist (self):
        data = json.dumps({
            "name": "Billboards TOP 100",
            "description": "Billboard Top 100 chart tracks - updated weekly",
            "public": True
        })
        url_post = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        OAuth_token = os.getenv('OAuth_Create_Playlist')
        r = requests.post(url_post,
                          data,
                          headers= {
                              "Authorization": f"Bearer {OAuth_token}"
                          })
        r = r.json()
        print(r)

        playlist_id = r["id"]
        return playlist_id

    def populate_playlist (self, pid, data_list):
        track_uris = ['spotify:track:'+track[3] for track in data_list]
        data = json.dumps(track_uris)
        url_post = f"https://api.spotify.com/v1/playlists/{pid}/tracks"
        OAuth_token = os.getenv('OAuth_Populate_Playlist')
        r = requests.post(url_post, data,
                          headers={
                              "Authorization": f"Bearer {OAuth_token}"
                          })
        r = r.json()
        return r
    
    def get_playlist_items (self, pid, version='v1'):
        endpoint = f"https://api.spotify.com/{version}/playlists/{pid}/tracks"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            print(r)
            return {}

        data = r.json()
        track_ids = []

        for item in data['items']:
            track_ids.append(item['track']['id'])

        return track_ids

    def clear_playlist (self, pid):
        track_list = self.get_playlist_items(pid)
        track_uris = ["spotify:track:"+track for track in track_list]
        params = {"tracks": []}
        for uri in track_uris:
            params["tracks"].append({"uri": uri})

        #print(params)

        endpoint = f"https://api.spotify.com/v1/playlists/{pid}/tracks"
        OAuth_token = os.getenv('OAuth_delete_playlist')
        r = requests.delete(endpoint, headers={
            'Content-Type': 'apllication/JSON',
            'Authorization': f"Bearer {OAuth_token}"
        }, data=params)

        return r.json()

client = SpotifyAPI(client_id,client_secret)
print(client.perform_auth())


res = client.search(query='Sweater Weather',search_type='track')

for data in res["tracks"]["items"]:
    print(data["album"]["artists"][0]["name"], end=" ")
    print(data["id"])

scrape_list = Scrapper()
data_list = scrape_list.scrapped_data()


for l in data_list:
    track_data = l[1]
    artist_data = l[2]
    res = client.search(query=track_data, search_type='track')
    for data in res["tracks"]["items"]:
            l.append(data["id"])



# Create the playlist and use this code once. Then save the playlist ID.
# p_id = '2F7LKru4ouJQdrqkJlSFiC'

p_id = client.create_playlist()


playlist_status = client.populate_playlist(p_id, data_list)
#print(playlist_status)

print(client.clear_playlist(p_id, sample_tracks))

