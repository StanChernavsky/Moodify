import json
import numpy as np
from pprint import pprint

playlists = []
playlists.append(json.load(open('seed.json')))
playlists.append(json.load(open('seed2.json')))
playlists.append(json.load(open('seed3.json')))


track = json.load(open('track.json'))
audio_features_list = ['danceability', 'valence', 'energy', 'tempo']

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
   
weights = [.5, .3, .1, .1] 

avg_var_dicts = []

for playlist in playlists:
    avg_var_dicts.append(computeAverageAndVariance(playlist))

distances = []
minDist = float('inf')
minIdx = -1
print avg_var_dicts
print "---------------------- PRINTING LENGTH", len(avg_var_dicts)
for i, avg_var_dict in enumerate(avg_var_dicts):

    variances = [(feature, avg_var_dict[feature][1]) for feature in avg_var_dict]
    sorted_list_variances = sorted(variances, key=lambda x: x[1])

    variance_importance_dict = {}
    for j, (feature, variance) in enumerate(sorted_list_variances):
        variance_importance_dict[feature] = j

    dist = computeDistance(avg_var_dict, variance_importance_dict, track, weights)
    distances.append(dist)
    if minDist > dist:
        print minIdx, i
        minIdx = i
        minDist = dist


print sorted(distances)[0]
print minIdx




