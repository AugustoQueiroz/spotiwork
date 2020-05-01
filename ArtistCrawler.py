import os
import json
import base64
import requests
import argparse
import urllib.parse
import urllib.request

parser = argparse.ArgumentParser(description="""
        Build a network of artists starting from a source and crawling through spotify's 'Related Artists'.
        """
        )

parser.add_argument('-s', '--seed', dest='seed', help='The id of the artist to begin the crawler with', required=True)
parser.add_argument('-o', '--output', dest='out', help='The name of the file to which the network should be written')
parser.add_argument('-e', '--expand', dest='input', help='The name of the network file that should be expanded upon')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Verbose mode will print the names of the artists being added to the frontier, whereas non-verbose mode will only present the number of artists currently in the frontier and the number of artists already explored')

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

def load_network(input_file_path):
    frontier = set()
    explored = set()
    edges = set()

    with open(input_file_path) as input_file:
        for line in input_file:
            line = line.split()
            frontier.add(line[1])
            explored.add(line[0])
            edges.add((line[0], line[1]))

    frontier = frontier - explored

    return frontier, explored, edges

def crawl(seed_id, auth_token, token_type, output_file=None, frontier=set(), explored=set(), edges=set(), verbose=False):
    api_call_url = 'https://api.spotify.com/v1/artists/%s/related-artists'

    frontier.add(seed_id)
    while len(frontier) > 0:
        current_artist_id = frontier.pop()
        explored.add(current_artist_id)
        request = urllib.request.Request(api_call_url % current_artist_id, headers={
            'Content-Type': 'application/json',
            'Authorization': '%s %s' % (token_type, auth_token)
            })

        response = urllib.request.urlopen(request)
        response_body = json.loads(response.read().decode('latin-1'))

        try:
            for artist in response_body['artists']:
                if artist['id'] not in explored:
                    if verbose: print('Adding %s to frontier...' % artist['name'])
                    frontier.add(artist['id'])
                    edge = (current_artist_id, artist['id'])
                    edges.add(edge)
                    if output_file != None:
                        output_file.write('%s\t%s\n' % edge)
                if (artist['id'], current_artist_id) not in edges:
                    edges.add((current_artist_id, artist['id']))
        except KeyError:
            auth_token, token_type, _ = get_token(os.getenv('SPOTIFY_CLIENT_ID'), os.getenv('SPOTIFY_CLIENT_SECRET'))

        if not verbose: print('\rFrontier Size: %d | Explored Size: %d | Number of Edges: %d' % (len(frontier), len(explored), len(edges)), end='')

    print()

    return explored, edges

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

explored = set()
edges = set()

if args.input is not None:
    args.out = args.input
    frontier, explored, edges = load_network(args.input)

token, token_type, expiration = get_token(client_id, client_secret)
print(args.out)
with open(args.out, 'w' if args.input is None else 'a') as output_file:
    visited_artists, network = crawl(args.seed, token, token_type, output_file, frontier=frontier, explored=explored, edges=edges, verbose=args.verbose)
