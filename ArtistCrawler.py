import os
import json
import base64
import requests
import argparse
import urllib.error
import urllib.parse
import urllib.request

from spotify import Spotify

# Parsing Command-Line Arguments ###########################################################################
parser = argparse.ArgumentParser(description="""
        Build a network of artists starting from a source and crawling through spotify's 'Related Artists'.
        """
        )

parser.add_argument('-s', '--seed', dest='seed', help='The id of the artist to begin the crawler with', required=True)
parser.add_argument('-o', '--output', dest='out', help='The name of the file to which the network should be written')
parser.add_argument('-e', '--expand', dest='input', help='The name of the network file that should be expanded upon')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Verbose mode will print the names of the artists being added to the frontier, whereas non-verbose mode will only present the number of artists currently in the frontier and the number of artists already explored')

args = parser.parse_args()
############################################################################################################


def load_network(input_file_path):
    frontier = set()
    explored = set()
    edges = set()

    with open(input_file_path) as input_file:
        for line in input_file: # Each line in the file represents an edge of the network
            line = line.split()
            frontier.add(line[1])
            explored.add(line[0])
            edges.add((line[0], line[1]))

    frontier = frontier - explored

    return frontier, explored, edges

def crawl(seed_id, spotify, output_file=None, frontier=set(), explored=set(), edges=set(), verbose=False):
    # The api url with the spot where the artist ID should be subbed in

    # The frontier starts with the seed in
    frontier.add(seed_id)

    while len(frontier) > 0:
        current_artist_id = frontier.pop()  # Get one artist from the frontier
        explored.add(current_artist_id)     # Mark it as visited

        try:
            # Get their related artists from Spotify
            response = spotify.get_related_artists(current_artist_id)

            for artist in response['artists']:
                if artist['id'] not in explored:
                    if verbose: print('Adding %s to frontier...' % artist['name'])
                    frontier.add(artist['id'])
                    edge = (current_artist_id, artist['id'])
                    edges.add(edge)
                    if output_file != None:
                        output_file.write('%s\t%s\n' % edge)
                if (artist['id'], current_artist_id) not in edges: 
                    # If the related artist has been explored but isn't connected to the current artist
                    edges.add((current_artist_id, artist['id']))
        except (KeyError, urllib.error.HTTPError) as e: # If the authentication key expired, get a new one
            # TODO - This should be done differently, probably going to wrap the whole thing in a class
            spotify.token, spotify.token_type, _ = spotify.get_token(os.getenv('SPOTIFY_CLIENT_ID'), os.getenv('SPOTIFY_CLIENT_SECRET'))
            # Add the current id back into the frontier and go again
            frontier.add(current_artist_id)
            continue

        if not verbose: print('\rFrontier Size: %d | Explored Size: %d | Number of Edges: %d' % (len(frontier), len(explored), len(edges)), end='')

    print()

    return explored, edges

# Get the client id and secret from the environment
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

spotify = Spotify(client_id, client_secret)

frontier = set()
explored = set()
edges = set()
if args.input is not None: # If is expanding a partial network
    args.out = args.input # The input network should also be the output (expanding it!)
    frontier, explored, edges = load_network(args.input)

with open(args.out, 'w' if args.input is None else 'a') as output_file:
    visited_artists, network = crawl(args.seed, spotify, output_file, frontier=frontier, explored=explored, edges=edges, verbose=args.verbose)
