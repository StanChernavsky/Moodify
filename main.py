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
MAX_ITERS = 100
K = 4
centroids = {}
playlist_for_centroid = []

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
# return: dict from playlist to a list of audio features
def get_audio_features_for_playlists(playlists):
    playlist_dict = {}
    for playlist_id in playlists:
        print "***************** NEW PLAYLIST **************"
        playlist_dict[playlist_id] = []
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

        # dictionary of playlistIDs to tracks
        seed_playlists_w_audio_features = get_audio_features_for_playlists(processed_playlists)
        setUpCentroids(seed_playlists_w_audio_features)

        # introduce a new set of songs
        # NEW TRACKS DOESN'T EXIST YET
        introduceNewTracks(new_tracks)
        for iter_idx in xrange(MAX_ITERS):
            updateCentroids()
            #for each song, we assign new centroid, update playlist_for_centroid 
            new_playlist_for_centroid = [[]*K]
            for playlist in playlist_for_centroid:
                for track in playlist:
                    idx = assignTrackToCentroid(track)
                    new_playlist_for_centroid[idx].append(track)
            if centroids_not_changed(new_playlist_for_centroid):
                break
            #compare assignment with prev assignment, break if same 

        


        # run_clustering(processed_playlists)
        # print playlists
        # centroids = assignCentroids(playlists['items'])
    else:
        print "Can't get token for", username

def centroids_not_changed(new_playlist_for_centroid):
    for idx in xrange(K):
        if cmp(playlist_for_centroid, new_playlist_for_centroid) != 0:
            return False
    return True


# TODO when introducing new tracks; make sure they're incorporated in the centroid_dicts
# ASSUMES THAT NEW_TRACKS IS A LIST DAMMIT
def introduceNewTracks(new_tracks):
    new_track_assignments = []
    for track in new_tracks:
        idx = assignTrackToCentroid(track)
        playlist_for_centroid[idx].append(track)
        #TODO 



def assignTrackToCentroid(track):
    min_distance = float("inf")
    min_idx = -1
    for centroid in centroids:
        curr_distance = computeDistance(centroids[centroid], track)
        if min_distance > curr_distance:
            min_distance = curr_distance
            min_idx = centroid
    return min_idx

# playlist: a list of tracks (with audio features in them)
# avg_var_dict: dictionary key: feature name, value: (average, variance)
def computeCentroid(idx, playlist):
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

    corresponding_list_of_tracks_for_centroid[idx] = playlist
    #dictionary: feature key: (avg, var)
    return avg_var_dict

# 
def computeDistance(avg_var_dict, track):
    sum_so_far = 0
    for feature in track:
        if feature not in audio_features_list:
            continue
        sum_so_far += ((avg_var_dict[feature][0] - track[feature])**2) / (avg_var_dict[feature][1])
    return sum_so_far**0.5

# assumes that playlists is a list of list of tracks
def setUpCentroids(playlists_w_audio_features):
    for idx, playlist_id in enumerate(playlists_w_audio_features):
        curr_playlist = playlists_w_audio_features[playlist_id]
        centroid = computeCentroid(idx, curr_playlist)
        playlist_for_centroid[idx] = curr_playlist
        centroids[idx] = centroid

def updateCentroids():
    new_playlist_for_centroid
    for idx, playlist in enumerate(playlist_for_centroid):
        centroid = computeCentroid(idx, playlist)
        centroids[idx] = centroid





