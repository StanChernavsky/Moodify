import json
import numpy as np
from pprint import pprint
import sys
import client as client
import spotipy.util as util
import random
import math


audio_features_list = [u'danceability', u'valence', u'energy', u'tempo', u'loudness', u'acousticness', u'speechiness', u'liveness', 'release_decade', 'explicit']
feature_weight = {u'danceability': 1, u'valence': 1, u'energy':1 , u'tempo':1, u'loudness':1, u'acousticness':1, u'speechiness':1, u'liveness':1, 'release_decade':0, 'explicit':0}
MAX_ITERS = 5
K = 4
centroids = {}
playlist_for_centroid = [[] for i in range(K)]
tracks_dict = {}
playlist_id_to_name = {}

playlist_titles = ["Danceable", "Classical", "XXX", "Country", "Clusterfuck"]

def getTrackIds(tracks):
    track_ids = []
    for i, item in enumerate(tracks['items']):
        track = item['track']
        track_ids.append(track['id'])
        tracks_dict[track['id']] = (track['name'], track['artists'][0]['name'])
    return track_ids

# returns a dict of playlist ID to a list of track IDs
def process_playlists(sp, username, playlists):
    all_playlists = {}
    new_tracks_assigned = False
    new_tracks = {}
    k_so_far = 0
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            if playlist['name'] not in playlist_titles:
                continue
            else:
                print "added", playlist['name']
            playlist_id_to_name[playlist['id']] = playlist['name']
            if playlist['name'] == "Clusterfuck":
                if playlist['id'] not in new_tracks:
                    new_tracks[playlist['id']] = []
                results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                print "\n"
                new_tracks[playlist['id']] = getTrackIds(tracks)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    new_tracks[playlist['id']].append(getTrackIds(tracks))
            # if k_so_far == K: # JUST TO LIMIT IT TO 3 PLAYLISTS FOR NOW
            #     break

            if playlist['id'] not in all_playlists:
                all_playlists[playlist['id']] = []
            #print
            # print playlist['name']
            # print '  total tracks', playlist['tracks']['total']
            results = sp.user_playlist(username, playlist['id'],
                fields="tracks,next")
            tracks = results['tracks']
            all_playlists[playlist['id']] = getTrackIds(tracks)
            while tracks['next']:
                tracks = sp.next(tracks)
                all_playlists[playlist['id']].append(getTrackIds(tracks))
            # k_so_far += 1
    print "************************************************"
    return (new_tracks, all_playlists)

def get_additional_features(sp, track_id):
    track = sp.track(track_id)
    album_id = track["album"]["id"]
    album = sp.album(album_id)
    # if album["release_date"] == None:
        # print "NO RELEASE DATE"
    # print album["release_date"][:3] + "0"
    explicit_score = 1 if track["explicit"] == True else 0
    # if explicit_score == 1:
        # print track["name"]
    return 2020 - int(album["release_date"][:3] + "0"), explicit_score

# dict from playlist to track IDs
# return: dict from playlist id to a list of track audio features
# TODO: change to "features" than "audio features"
def get_audio_features_for_playlists(sp, playlists):
    playlist_dict = {}
    for playlist_id in playlists:

        # get all tracks from playlist
        tracks_in_playlist = []
        i = 0

        for track_id in playlists[playlist_id]:
            if track_id is None or type(track_id) == list:
                continue

            audio_features = sp.audio_features(tracks=[track_id])
            if audio_features[0] is None:
                print "audio features is empty:", playlist_id, playlist_id_to_name[playlist_id], track_id, tracks_dict[track_id]
            audio_features[0]['original_playlist_id'] = playlist_id

            if playlist_id_to_name[playlist_id] == "Clusterfuck":
                if i < 8:
                    audio_features[0]['correct_playlist'] = "Classical"
                elif i < 16:
                    audio_features[0]['correct_playlist'] = "Country"
                elif i < 24:
                    audio_features[0]['correct_playlist'] = "Lit"
                else:
                    audio_features[0]['correct_playlist'] = "XXX"
                i += 1

            audio_features[0]['release_decade'], audio_features[0]['explicit'] = get_additional_features(sp, track_id)
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
    # print "***ASSIGNED to"
    # print min_idx
    # print "***\n"
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
    # print "*******COMPUTED CENTROID********"
    # print avg_var_dict
    # print "\n"
    return avg_var_dict


def computeDistance(avg_var_dict, track):
    sum_so_far = 0
    for feature in track:
        if feature not in audio_features_list:
            continue
        print "division by "
        print avg_var_dict[feature][1]
        sum_so_far += feature_weight[feature]* ((avg_var_dict[feature][0] - track[feature])**2) / (avg_var_dict[feature][1] + 1)
    # print "*******COMPUTED DISTANCE********"
    # print sum_so_far**0.5
    return sum_so_far**0.5



def updateCentroids():
    new_playlist_for_centroid = [[] for i in range(K)]
    #print "I AM IN UPDATE CENTROIDS AND I SHOULD BE AN L OF L OF DS", playlist_for_centroid
    for idx, list_of_dicts_playlist in enumerate(playlist_for_centroid):

        #print "I AM SUPPOSED TO BE A FUCKING LIST OF DICTIONARIES", list_of_dicts_playlist
        # playlist should be a list of dictionaries
        centroid = computeCentroid(idx, list_of_dicts_playlist)
        if len(centroid) == 0:
            print "CENTROID IS EMPTY! AVG VAR DICT IS EMPTY!", idx, list_of_dicts_playlist
        centroids[idx] = centroid



def centroids_not_changed(new_playlist_for_centroid):
    for idx in xrange(K):
        # print playlist_for_centroid, new_playlist_for_centroid
        if cmp(playlist_for_centroid, new_playlist_for_centroid) != 0:
            return False
    return True


# TODO when introducing new tracks; make sure they're incorporated in the centroid_dicts
# ASSUMES THAT NEW_TRACKS IS A LIST DAMMIT
def introduceNewTracks(new_tracks):
    for track in new_tracks:
        if type(track) != dict:
            continue
        idx = assignTrackToCentroid(track)
        playlist_for_centroid[idx].append(track)
        #TODO


#idx index of the centroid that has to be randomized
def get_random_centroid(idx):
    # print "WE ARE INSIDE GET RANDOM CENTROID!"
    # print "playlist_for_centroid type:", type(playlist_for_centroid), " ||| ", playlist_for_centroid
   # print ""
    centroid = {}
    playlist_index = random.randint(0, len(playlist_for_centroid)-1)
    while (len(playlist_for_centroid[playlist_index]) < 3):
        playlist_index = random.randint(0, len(playlist_for_centroid)-1)

    song_index = random.randint(0, len(playlist_for_centroid[playlist_index])-2)
    while type(playlist_for_centroid[playlist_index][song_index]) != dict :
        song_index = random.randint(0, len(playlist_for_centroid[playlist_index])-2)
    for feature in audio_features_list:
        centroid[feature] = (playlist_for_centroid[playlist_index][song_index][feature], 0)
    playlist_for_centroid[idx].append(playlist_for_centroid[playlist_index][song_index])
    del playlist_for_centroid[playlist_index][song_index]
    return centroid

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

        # print "******************************* PROCESSED PLAYLISTS", processed_playlists # playlist id to tracks
        # get audio features

        # dictionary of playlistIDs to tracks

        seed_playlists_w_audio_features = get_audio_features_for_playlists(sp, processed_playlists)
        # print "PRINTING SEED PLAYLIST", seed_playlists_w_audio_features
        setUpCentroids(seed_playlists_w_audio_features)

        # introduce a new set of songs
        # NEW TRACKS DOESN'T EXIST YET
        introduceNewTracks(new_tracks)
        for iter_idx in xrange(MAX_ITERS):
            print "******************centroids", centroids
            updateCentroids()
            #for each song, we assign new centroid, update playlist_for_centroid
            new_playlist_for_centroid = [[] for i in range(K)]
            for playlist in playlist_for_centroid:
                for track in playlist:
                    idx = assignTrackToCentroid(track)
                    new_playlist_for_centroid[idx].append(track)
            if centroids_not_changed(new_playlist_for_centroid):
                break

            empty_cluster_indices = []
            #print "NEW PLAYLIST FOR CENTROID", new_playlist_for_centroid
            for i, new_p in enumerate(new_playlist_for_centroid):
                if len(new_p) == 0:
                    empty_cluster_indices.append(i)

            # print "THESE ARE THE EMPTY CLUSTER INDICES:", empty_cluster_indices
            # print "CENTROIDS", centroids

            playlist_for_centroid = new_playlist_for_centroid

            for idx in empty_cluster_indices:
                centroids[idx] = get_random_centroid(idx)



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
