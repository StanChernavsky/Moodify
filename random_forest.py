import json
import numpy as np
import pandas as pd
from pprint import pprint
import sys
import client as client
import spotipy.util as util
import random
from sklearn import tree
import itertools
import csv
from sklearn.metrics import confusion_matrix
import time
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns


audio_features_list = [u'danceability', u'valence', u'energy', u'tempo', u'loudness', u'acousticness', u'speechiness', u'liveness']
MAX_ITERS = 1000
K = 4
centroids = {}
playlist_for_centroid = [[] for i in range(K)]
tracks_dict = {}

playlist_titles = ["Lit", "Classical", "XXX", "Country", "Clusterfuck"]
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
                continue
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
    ######print "************************************************"
    ######print new_tracks, all_playlists
    return (new_tracks, all_playlists)

# dict from playlist to track IDs
# return: dict from playlist id to a list of [dicts that hold audio features] for each track
def get_audio_features_for_playlists(sp, playlists):
    playlist_dict = {}
    for playlist_id in playlists:
        # print playlists[playlist_id]

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
                if i < 25:
                    audio_features[0]['correct_playlist'] = "Country"
                elif i < 50:
                    audio_features[0]['correct_playlist'] = "XXX"
                elif i < 75:
                    audio_features[0]['correct_playlist'] = "Lit"
                else:
                    audio_features[0]['correct_playlist'] = "Classical"
                i += 1



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


def findsubsets(S,m):
    return set(itertools.combinations(S, m))
# TODO when introducing new tracks; make sure they're incorporated in the centroid_dicts
# ASSUMES THAT NEW_TRACKS IS A LIST DAMMIT
def introduceNewTracks(new_tracks):
    for track in new_tracks:
        if type(track) != dict:
            continue
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

        # create a dict of playlist ID to a list of track IDs
        (new_tracks, processed_playlists) = process_playlists(sp, username, playlists)

        # dict from playlist id to a list of dicts of track_idx : audio features dict
        seed_playlists_w_audio_features = get_audio_features_for_playlists(sp, processed_playlists)
        # print seed_playlists_w_audio_features

        print "******ABOUT TO START DATAFRAME******"

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

        print "DF TEST *********"
        print df_test

        ########Now we have a DataFrame where each row is a different track###########
        ######RANDOM FOREST STUFF############

        # Train the Classifier to take training features and learn how they
        # relate to actual output y
        clf = RandomForestClassifier(n_jobs=2, random_state=0)
        
        # Train the classifier
        clf.fit(df_train[audio_features_list], df_train['original_playlist_id'])

        # Apply classifier to test data
        predictions = clf.predict(df_test[audio_features_list])

        # Show how with what probability the classifier thinks each track 
        # should belong to each category
        print "********PREDICTION PROBABILITIES*********"
        print clf.predict_proba(df_test[audio_features_list])

        # Convert playlist_ids to names
        for i, id in enumerate(predictions):
            predictions[i] = playlist_id_to_name[id].encode('UTF-8')

        # Evaluate classifier
        print "*********PLAYLIST PREDICTIONS FOR TEST SET**********"
        print predictions

        print "*********CORRECT PLAYLISTS FOR TEST SET*********"
        test_correct_playlists = df_test["correct_playlist"].tolist()
        print test_correct_playlists

        correct_count_classical = 0
        correct_count_lit = 0
        correct_count_sensual = 0
        correct_count_country = 0
        total_count_classical = 0
        total_count_lit = 0
        total_count_sensual = 0
        total_count_country = 0

        num_tracks = len(test_correct_playlists)
        for i in range(num_tracks):
            if test_correct_playlists[i] == "Classical":
                if predictions[i] == test_correct_playlists[i]:
                    correct_count_classical += 1
                total_count_classical += 1

            if test_correct_playlists[i] == "Lit":
                if predictions[i] == test_correct_playlists[i]:
                    correct_count_lit += 1
                total_count_lit += 1

            if test_correct_playlists[i] == "XXX":
                if predictions[i] == test_correct_playlists[i]:
                    correct_count_sensual += 1
                total_count_sensual += 1


            if test_correct_playlists[i] == "Country":
                if predictions[i] == test_correct_playlists[i]:
                    correct_count_country += 1
                total_count_country += 1

        correct_count_classical /= float(total_count_classical)
        correct_count_lit /= float(total_count_lit)
        correct_count_sensual /= float(total_count_sensual)
        correct_count_country /= float(total_count_country)

        print "*********ACCURACY FOR RANDOM FOREST************"
        print "True positive classical: ", correct_count_classical
        print "True positive lit: ", correct_count_lit
        print "True positive sensual: ", correct_count_sensual
        print "True positive country: ", correct_count_country

        # Confusion matrix
        y_true = test_correct_playlists
        y_pred = predictions
        conf_mat = confusion_matrix(y_true, y_pred)
        conf_mat_plot = sns.heatmap(conf_mat.T, square=True, annot=True, fmt='d', cbar=False, 
                    xticklabels=["Classical", "Country", "Lit", "Sensual"], yticklabels=["Classical", "Country", "Lit", "Sensual"]).set_title("Confusion matrix for Random Forest")
        conf_mat_plot.figure.savefig("confusion-matrix-random-forest.png")

    else:
        print "Can't get token for", username
