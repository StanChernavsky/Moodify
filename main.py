import json
import numpy as np
from pprint import pprint
import sys
import client as client
import spotipy.util as util

# for testing without oauth
# playlists = []
# playlists.append(json.load(open('seed.json')))
# playlists.append(json.load(open('seed2.json')))
# playlists.append(json.load(open('seed3.json')))

# track = json.load(open('track.json'))
audio_features_list = ['danceability', 'valence', 'energy', 'tempo', 'loudness', 'acousticness', 'speechiness', 'liveness']
MAX_ITERS = 300
K = 3
centroids = {}
playlist_for_centroid = [[] for i in range(K)]
tracks_dict = {}

def getTrackIds(tracks):
    track_ids = []
    for i, item in enumerate(tracks['items']):
        track = item['track']
        # print track
        track_ids.append(track['id'])
        tracks_dict[track['id']] = (track['name'], track['artists'][0]['name'])
    return track_ids

# returns a dict of playlist ID to a list of track IDs
def process_playlists(sp, username, playlists):
    all_playlists = {}
    new_tracks_assigned = False
    new_tracks = {}
    k_so_far = 0
    i = 0
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            if i == 0:
                if playlist['id'] not in new_tracks:
                    new_tracks[playlist['id']] = []
                results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                new_tracks[playlist['id']] = getTrackIds(tracks)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    new_tracks[playlist['id']].append(getTrackIds(tracks))
                i += 1
                continue
            if k_so_far == K: # JUST TO LIMIT IT TO 3 PLAYLISTS FOR NOW
                break
            
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
            k_so_far += 1
            i += 1
    print "************************************************"
    return (new_tracks, all_playlists)

# dict from playlist to track IDs
# return: dict from playlist to a list of audio features
def get_audio_features_for_playlists(sp, playlists):
    playlist_dict = {}
    for playlist_id in playlists:
        # print playlists[playlist_id]

        # get all tracks from playlist
        tracks_in_playlist = []

        for track_id in playlists[playlist_id]:
            if track_id is None or type(track_id) == list:
                continue
            audio_features = sp.audio_features(tracks=[track_id])
            tracks_in_playlist.append(audio_features[0])
        playlist_dict[playlist_id] = tracks_in_playlist
    return playlist_dict

# assumes that playlists is a list of list of tracks
def setUpCentroids(playlists_w_audio_features):
    for idx, playlist_id in enumerate(playlists_w_audio_features):
        curr_playlist = playlists_w_audio_features[playlist_id]
        centroid = computeCentroid(idx, curr_playlist)
        playlist_for_centroid[idx] = curr_playlist
        centroids[idx] = centroid

def assignTrackToCentroid(track):
    min_distance = float("inf")
    min_idx = -1
    if len(centroids) == 0:
        print "centroids length is 0 even though it's not supposed to be!"
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
    
    for track in playlist:
        for feature in track: # each track is made up of only features
            if feature not in audio_features_list:
                continue
            if feature not in features:
                features[feature] = []
            features[feature].append(track[feature])

    avg_dict = {}
    avg_var_dict = {}
    for feature in features:
        avg_var_dict[feature] = (np.mean(features[feature]), np.var(features[feature]))

    playlist_for_centroid[idx] = playlist
    #dictionary: feature key: (avg, var)
    return avg_var_dict


def computeDistance(avg_var_dict, track):
    sum_so_far = 0
    for feature in track:
        if feature not in audio_features_list:
            continue
        sum_so_far += ((avg_var_dict[feature][0] - track[feature])**2) / (avg_var_dict[feature][1])
    return sum_so_far**0.5



def updateCentroids():
    new_playlist_for_centroid = [[] for i in range(K)]
    for idx, playlist in enumerate(playlist_for_centroid):
        centroid = computeCentroid(idx, playlist)
        if len(centroid) == 0:
            print "CENTROID IS EMPTY! AVG VAR DICT IS EMPTY!", idx, playlist
        centroids[idx] = centroid



def centroids_not_changed(new_playlist_for_centroid):
    for idx in xrange(K):
        print playlist_for_centroid, new_playlist_for_centroid
        if cmp(playlist_for_centroid, new_playlist_for_centroid) != 0:
            return False
    return True


# TODO when introducing new tracks; make sure they're incorporated in the centroid_dicts
# ASSUMES THAT NEW_TRACKS IS A LIST DAMMIT
def introduceNewTracks(new_tracks):
    for track in new_tracks:
        idx = assignTrackToCentroid(track)
        playlist_for_centroid[idx].append(track)
        #TODO 







if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Whoops, need your username!"
        print "usage: python user_playlists.py [username]"
        sys.exit()

    token = util.prompt_for_user_token(username)

    if token:
        sp = client.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        # processed_playlists is a dict from playlist ID to track IDs
        (new_tracks, processed_playlists) = process_playlists(sp, username, playlists)

        print "******************************* PROCESSED PLAYLISTS", processed_playlists # playlist id to tracks
        # get audio features

        # dictionary of playlistIDs to tracks

        seed_playlists_w_audio_features = get_audio_features_for_playlists(sp, processed_playlists)
        # print "PRINTING SEED PLAYLIST", seed_playlists_w_audio_features
        setUpCentroids(seed_playlists_w_audio_features)

        # introduce a new set of songs
        # NEW TRACKS DOESN'T EXIST YET
        introduceNewTracks(new_tracks)
        for iter_idx in xrange(MAX_ITERS):
            updateCentroids()
            #for each song, we assign new centroid, update playlist_for_centroid 
            new_playlist_for_centroid = [[] for i in range(K)]
            for playlist in playlist_for_centroid:
                for track in playlist:
                    idx = assignTrackToCentroid(track)
                    new_playlist_for_centroid[idx].append(track)
            if centroids_not_changed(new_playlist_for_centroid):
                break
            #compare assignment with prev assignment, break if same 

        print "******************* final result ******************* after", iter_idx, "iterations"
        for i, p in enumerate(playlist_for_centroid):
            print "******************* CENTROID", i, "****************************"
            for track in p:
                if type(track) != dict:
                    continue
                if track['id'] in tracks_dict:
                    print tracks_dict[track['id']]
            print "********* average, variance dictionary *********"
            print computeCentroid(i, p)
            print "******************************************************************"
    else:
        print "Can't get token for", username





