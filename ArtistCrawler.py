import os
import json
import base64
import requests
import argparse
import urllib.parse
import urllib.request

parser = argparse.ArgumentParser(description="""
        Build a network of artists from a source by skipping through related artists.
        """
        )

parser.add_argument('-s', '--seed', dest='seed', help='The id of the artist to begin the crawler with.')
parser.add_argument('-o', '--output', dest='out', help='The name of the file to which the network should be written')

args = parser.parse_args()

def get_token(client_id, client_secret):
    api_call_url = 'https://accounts.spotify.com/api/token'

    authorization = 'Basic %s' % (base64.b64encode(('%s:%s' % (client_id, client_secret)).encode('utf-8')).decode('latin-1'))

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

    return response_body['access_token'], response_body['token_type'], response_body['expires_in']

def crawl(seed_id, auth_token, token_type, output_file=None):
    api_call_url = 'https://api.spotify.com/v1/artists/%s/related-artists'

    frontier = set([seed_id])
    explored = set()
    edges = set()
    while len(frontier) > 0:
        current_artist_id = frontier.pop()
        explored.add(current_artist_id)
        request = urllib.request.Request(api_call_url % current_artist_id, headers={
            'Content-Type': 'application/json',
            'Authorization': '%s %s' % (token_type, auth_token)
            })

        response = urllib.request.urlopen(request)
        response_body = json.loads(response.read().decode('latin-1'))

        for artist in response_body['artists']:
            if artist['id'] not in explored:
                print('Adding %s to frontier...' % artist['name'])
                frontier.add(artist['id'])
                edge = (current_artist_id, artist['id'])
                edges.add(edge)
                if output_file != None:
                    output_file.write('%s\t%s\n' % edge)

    return explored, edges

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

token, token_type, expiration = get_token(client_id, client_secret)
with open(args.out, 'w') as output_file:
    visited_artists, network = crawl(args.seed, token, token_type, output_file)
