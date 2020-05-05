import os
import argparse
import itertools
import urllib.error

from spotify import Spotify

parser = argparse.ArgumentParser()

parser.add_argument('-a', '--artist-network', dest='artist_network', required=True)

args = parser.parse_args()

def load_artists(artist_network_path):
    artist_ids = set()
    with open(artist_network_path) as artist_network:
        for line in artist_network:
            artist_ids.update(line.split())

    return list(artist_ids)

def build_genre_network(spotify, artist_ids, out_file=None):
    i = 0
    edges = set()
    while len(artist_ids) - i > 0:
        try:
            artist_infos = spotify.get_several_artists(artist_ids[i:i + min(50, len(artist_ids)-i)])
        except urllib.error.HTTPError:
            spotify.token, spotify.token_type, _ = spotify.get_token()
            continue

        new_edges = []
        for artist in artist_infos:
            new_edges += itertools.combinations(artist['genres'], 2)
            if out_file is not None:
                for edge in set(new_edges) - edges:
                    out_file.write('%s\t%s\n' % edge)
            edges.update(new_edges)

        i += 50
        print('\r%.2f%% of artists visited' % (i * 100.0 / len(artist_ids)), end='')


artist_ids = load_artists(args.artist_network)

spotify = Spotify(os.getenv('SPOTIFY_CLIENT_ID'), os.getenv('SPOTIFY_CLIENT_SECRET'))
with open('genres.net', 'w') as genre_network:
    build_genre_network(spotify, artist_ids, genre_network)
