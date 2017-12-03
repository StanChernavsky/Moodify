import json
import numpy as np
import pandas as pd
from pprint import pprint
import sys
import client as client
import spotipy.util as util
import random
from sklearn.tree import DecisionTreeClassifier


audio_features_list = [u'danceability', u'valence', u'energy', u'tempo', u'loudness', u'acousticness', u'speechiness', u'liveness']
MAX_ITERS = 1000
K = 4
centroids = {}
playlist_for_centroid = [[] for i in range(K)]
tracks_dict = {}

playlist_titles = ["Danceable", "Classical", "XXX", "Country", "Clusterfuck"]
playlist_id_to_name = {}

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
                new_tracks[playlist['id']] = getTrackIds(tracks)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    new_tracks[playlist['id']].append(getTrackIds(tracks))
            if k_so_far == K: # JUST TO LIMIT IT TO 3 PLAYLISTS FOR NOW
                break

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
            k_so_far += 1
    print "************************************************"
    return (new_tracks, all_playlists)

# dict from playlist to track IDs
# return: dict from playlist id to a list of track audio features
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
            audio_features[0]['original_playlist_id'] = playlist_id
            tracks_in_playlist.append(audio_features[0])
        playlist_dict[playlist_id] = tracks_in_playlist
    # print "PRINTING PLAYLIST DICT *********************", playlist_dict
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
    # print "PRINTING OUT AVG_VAR_DICT", avg_var_dict
    #print "printing out track", track
    for feature in track:
       # print "printing out feature", feature
        if feature not in audio_features_list:
            continue
        sum_so_far += ((avg_var_dict[feature][0] - track[feature])**2) / (avg_var_dict[feature][1])
    return sum_so_far**0.5



def updateCentroids():
    new_playlist_for_centroid = [[] for i in range(K)]
    print "I AM IN UPDATE CENTROIDS AND I SHOULD BE AN L OF L OF DS", playlist_for_centroid
    for idx, list_of_dicts_playlist in enumerate(playlist_for_centroid):

        print "I AM SUPPOSED TO BE A FUCKING LIST OF DICTIONARIES", list_of_dicts_playlist
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
    print "WE ARE INSIDE GET RANDOM CENTROID!"
    # print "playlist_for_centroid type:", type(playlist_for_centroid), " ||| ", playlist_for_centroid
   # print ""
    centroid = {}
    playlist_index = random.randint(0, len(playlist_for_centroid)-1)
    while (len(playlist_for_centroid[playlist_index]) < 3):
        playlist_index = random.randint(0, len(playlist_for_centroid)-1)
    # print "chosen playlist, I SHOULD BE A LIST OF DICTIONARIES", playlist_for_centroid[playlist_index]
    # print "****************"
    # print "printing length of playlists", len(playlists), "playlist index", playlist_index, "length of chosen playlist", playlists[playlist_index]
    # print "printing chosen playlist", playlists[playlist_index]
    song_index = random.randint(0, len(playlist_for_centroid[playlist_index])-2)
    while type(playlist_for_centroid[playlist_index][song_index]) != dict :
        song_index = random.randint(0, len(playlist_for_centroid[playlist_index])-2)
    for feature in audio_features_list:
        # print "******* playlist_index chosen", feature, playlist_for_centroid[playlist_index]
        # print "******** feature:", feature, playlist_for_centroid[playlist_index][song_index]
        # print "THIS SHOULD BE TRACK METADATA DICTIONARY", playlist_for_centroid[playlist_index][song_index]
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
        # new tracks should be songsTest
        (new_tracks, processed_playlists) = process_playlists(sp, username, playlists)

        # print "******************************* PROCESSED PLAYLISTS", processed_playlists # playlist id to tracks
        # get audio features

        # dictionary of playlistIDs to tracks

        #dict from playlist id to a list of track audio features
        seed_playlists_w_audio_features = get_audio_features_for_playlists(sp, processed_playlists)
        print seed_playlists_w_audio_features

        df_train = pd.DataFrame()

        for playlist_key in seed_playlists_w_audio_features:
            for track_idx, track_elem in enumerate(seed_playlists_w_audio_features[playlist_key]):
                #track_row = pd.DataFrame.from_dict(seed_playlists_w_audio_features[playlist_key][track_idx], index = [i])
                track_row = pd.Series(seed_playlists_w_audio_features[playlist_key][track_idx])
                # track_row = track_row.assign(original_playlist=pd.Series(playlist_key).values)
                df_train = df_train.append(track_row, ignore_index=True)

        
        print "DF TRAIN ********"
        print df_train

        df_test_with_audio_features = get_audio_features_for_playlists(sp, new_tracks)
        df_test = pd.DataFrame()
        for playlist_key in df_test_with_audio_features:
            for track_idx, track_elem in enumerate(df_test_with_audio_features[playlist_key]):
                track_row = pd.Series(df_test_with_audio_features[playlist_key][track_idx])
                df_test = df_test.append(track_row, ignore_index=True)
        # print "PRINTING SEED PLAYLIST", seed_playlists_w_audio_features



        # f = open('songs.csv','rU')
        # songs = pd.read_csv(f)

        # songsTrain and songsTest

        # Predict temperature category from other features

        # citiesTrain: all songs
        # citiesTest: new playlist
        features = audio_features_list
        split = 10
        dt = DecisionTreeClassifier(min_samples_split=split) # parameter is optional
        dt.fit(df_train[features],df_train['original_playlist_id']) #category is playlist ID
        predictions = dt.predict(df_test[features])

        print "******************* final result *******************"
        for prediction in predictions:
            print playlist_id_to_name[prediction]
        # Calculate accuracy
        # numtrain = len(songsTrain)
        # numtest = len(songsTest)
        # correct = 0
        # for i in range(numtest):
        #     print 'Predicted:', predictions[i], ' Actual:', citiesTest.loc[numtrain+i]['category']
        #     if predictions[i] == citiesTest.loc[numtrain+i]['category']: correct +=1
        # print 'Accuracy:', float(correct)/float(numtest)
        

    else:
        print "Can't get token for", username
