import json
import numpy as np
from pprint import pprint
import sys
import spotipy
import spotipy.util as util

# for testing without oauth
# playlists = []
# playlists.append(json.load(open('seed.json')))
# playlists.append(json.load(open('seed2.json')))
# playlists.append(json.load(open('seed3.json')))

# track = json.load(open('track.json'))
audio_features_list = ['danceability', 'valence', 'energy', 'tempo']




def getTrackIds(tracks):
    track_ids = []
    for i, item in enumerate(tracks['items']):
        track = item['track']
        track_ids.append(track['id'])
    return track_ids

# returns a dict of playlist ID to a list of track IDs
def process_playlists(username, playlists):
    all_playlists = {}
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            if playlist['id'] not in all_playlists:
                all_playlists[playlist['id']] = []
            print
            print playlist['name']
            print '  total tracks', playlist['tracks']['total']
            results = sp.user_playlist(username, playlist['id'],
                fields="tracks,next")
            tracks = results['tracks']
            all_playlists[playlist['id']] = getTrackIds(tracks)
            while tracks['next']:
                tracks = sp.next(tracks)
                all_playlists[playlist['id']].append(getTrackIds(tracks))
    print "************************************************"
    return all_playlists

# dict from playlist to track IDs
def get_audio_features_for_playlists(playlists):
    print "NEW TRACK *************"
    tracks_list = []
    for playlist_id in playlists:
        for track_id in playlists[playlist_id]:
            print track_id
    return tracks_list


if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Whoops, need your username!"
        print "usage: python user_playlists.py [username]"
        sys.exit()

    token = util.prompt_for_user_token(username)

    if token:
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        # processed_playlists is a dict from playlist ID to track IDs
        processed_playlists = process_playlists(username, playlists)

        print "******************************* PROCESSED PLAYLISTS", processed_playlists
        # get audio features
        playlists_w_audio_features = get_audio_features_for_playlists(processed_playlists)
        # run_clustering(processed_playlists)
        # print playlists
        # centroids = assignCentroids(playlists['items'])
    else:
        print "Can't get token for", username






# playlist: dictionary loaded from json file
def computeAverageAndVariance(playlist):
    features = {}
    # print "printing playlist-----------------------"
    # print playlist
    
    for track in playlist:
        # print track['name']
        for feature in track: # each track is made up of only features

            if feature not in audio_features_list:
                continue
            if feature not in features:
                features[feature] = []
            features[feature].append(track[feature])

    avg_dict = {}
    variance_dict = {}
    #print features
    avg_var_dict = {}
    for feature in features:
        avg_var_dict[feature] = (np.mean(features[feature]), np.var(features[feature]))

    #dictionary: feature key: (avg, var)
    return avg_var_dict

def computeDistance(avg_var_list, variance_importance_dict, track, weights):
    sum_so_far = 0
    for feature in track:
        if feature not in audio_features_list:
            continue
        importance_idx = variance_importance_dict[feature]
        weight = weights[importance_idx]
        sum_so_far += weight*(avg_var_dict[feature][0] - track[feature])**2
    return sum_so_far**0.5
   

# assumes that playlists is a list of list of tracks
def assignCentroids(playlists):
    weights = [.5, .3, .1, .1] 

    avg_var_dicts = []

    for playlist in playlists:
        avg_var_dicts.append(computeAverageAndVariance(playlist))

    distances = []
    minDist = float('inf')
    minIdx = -1
    return avg_var_dicts

def assignTrackToCentroid(track, playlist_centroids):
    print "---------------------- # OF PLAYLISTS:", len(avg_var_dicts), "-------------------"
    for i, playlist_centroid in enumerate(playlist_centroids):

        variances = [(feature, playlist_centroid[feature][1]) for feature in playlist_centroid]
        sorted_list_variances = sorted(variances, key=lambda x: x[1])

        variance_importance_dict = {}
        for j, (feature, variance) in enumerate(sorted_list_variances):
            variance_importance_dict[feature] = j

        dist = computeDistance(playlist_centroid, variance_importance_dict, track, weights)
        distances.append(dist)
        if minDist > dist:
            print minIdx, i
            minIdx = i
            minDist = dist


    print sorted(distances)[0]
    print minIdx




