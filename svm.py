import json
import numpy as np
import pandas as pd
from pprint import pprint
import sys
import client as client
import spotipy.util as util
import random
from sklearn import tree, linear_model, svm
import itertools
import csv
from sklearn.metrics import confusion_matrix


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

def trainForEachPlaylist(seed_playlists_w_audio_features):
    df_train = pd.DataFrame()
    df_train_label = pd.DataFrame()

    for playlist_key in seed_playlists_w_audio_features:
        for track_idx, track_elem in enumerate(seed_playlists_w_audio_features[playlist_key]):
            #track_row = pd.DataFrame.from_dict(seed_playlists_w_audio_features[playlist_key][track_idx], index = [i])
            track_row = pd.Series(seed_playlists_w_audio_features[playlist_key][track_idx])
            # track_row = track_row.assign(original_playlist=pd.Series(playlist_key).values)
            df_train = df_train.append(track_row, ignore_index=True)
            df_train_label = df_train_label.append(pd.Series(playlist_id_to_name[playlist_key]), ignore_index=True)

    df_train = df_train[[u'danceability', u'valence', u'energy', u'tempo', u'loudness', u'acousticness', u'speechiness', u'liveness']]

    # print "DF TRAIN LABEL", playlist_title, "********"
    # print df_train_label

    df_test_with_audio_features = get_audio_features_for_playlists(sp, new_tracks)
    df_test = pd.DataFrame()
    for playlist_key in df_test_with_audio_features:
        for track_idx, track_elem in enumerate(df_test_with_audio_features[playlist_key]):
            track_row = pd.Series(df_test_with_audio_features[playlist_key][track_idx])
            df_test = df_test.append(track_row, ignore_index=True)
    df_test_features_only = df_test[[u'danceability', u'valence', u'energy', u'tempo', u'loudness', u'acousticness', u'speechiness', u'liveness']]
    
    clf = svm.SVC()

    clf.fit(df_train, df_train_label.values.ravel())

    svm_res = clf.predict(df_test_features_only)
    i = 0
    correct = 0
    correct_for_each_playlist = {"Lit":0, "Classical":0, "XXX":0, "Country":0}
    y_true = [0] * 32
    for idx, df_test_row in df_test.iterrows():
        print tracks_dict[df_test_row['id']], "|||", \
        "correct: ", df_test_row['correct_playlist'], "|||", \
        "predicted:", svm_res[i]
        y_true[i] = df_test_row['correct_playlist']
        if (df_test_row['correct_playlist'] == svm_res[i]):
            correct_for_each_playlist[df_test_row['correct_playlist']] += 1
            correct += 1
        i += 1
    
    print "# CORRECT:", correct, "ACCURACY SCORE:", float(correct)/32

    for entry_key in correct_for_each_playlist:
        correct_for_each_playlist[entry_key] /= 8.0

    print correct_for_each_playlist
    with open('true-positives-svm.csv', 'w') as csvfile:
        fieldnames = ["Lit", "Classical", "XXX", "Country"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow(correct_for_each_playlist)
    y_pred = svm_res
    conf_mat = confusion_matrix(y_true, y_pred)

    with open('confusion-matrix-svm.csv', 'w') as f:
        f.write(np.array2string(conf_mat, separator=', '))


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
        (new_tracks, processed_playlists) = process_playlists(sp, username, playlists)

        #dict from playlist id to a list of track audio features
        seed_playlists_w_audio_features = get_audio_features_for_playlists(sp, processed_playlists)
        print seed_playlists_w_audio_features

        #for playlist_title in playlist_titles:
        trainForEachPlaylist(seed_playlists_w_audio_features)

    else:
        print "Can't get token for", username
