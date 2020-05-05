import requests
import urllib
import base64
import json

class Spotify:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

        self.token, self.token_type, self.token_expiration = self.get_token()

        self.api_base_url = 'https://api.spotify.com/v1/'

    def get_token(self):
        api_call_url = 'https://accounts.spotify.com/api/token'

        # Base64 encoded client_id:client_secret
        authorization = 'Basic %s' % (base64.b64encode(('%s:%s' % (self.client_id, self.client_secret)).encode('utf-8')).decode('latin-1'))

        # Make request
        response = requests.post(api_call_url,
                data={
                    'grant_type': 'client_credentials'
                    },
                headers={
                    'Authorization': authorization,
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                    })
        
        response_body = json.loads(response.text)

        # TODO - Remove the last one (not needed)
        return response_body['access_token'], response_body['token_type'], response_body['expires_in']

    def get_related_artists(self, artist_id):
        api_call_url = 'artists/%s/related-artists'

        request = urllib.request.Request(self.api_base_url + api_call_url % artist_id, headers={
            'Content-Type': 'application/json',
            'Authorization': '%s %s' % (self.token_type, self.token)
            })
        response = urllib.request.urlopen(request)
        response_body = json.loads(response.read().decode('latin-1'))

        return response_body['artists']

    def get_several_artists(self, artist_ids):
        if len(artist_ids) > 50:
            return None # TODO - Make this better

        api_call_url = 'artists?ids=%s'
    
        request = urllib.request.Request(self.api_base_url + api_call_url % ','.join(artist_ids),
                headers={
                    'Authorization': '%s %s' % (self.token_type, self.token)
                    })
        response = urllib.request.urlopen(request)
        response_body = json.loads(response.read().decode('latin-1'))

        return response_body['artists'] 
