# Into You = 1
# True Colors = 2
# Maggie Mae = 3
# Natural Science = 4
# Ay Vamos = 5

num_tracks = float(5)
num_surveys = float(10)

spotify_orderings = {}
spotify_orderings["danceability"] = [4, 3, 2, 5, 1]
spotify_orderings["valence"] = [4, 3, 2, 1, 5]
spotify_orderings["energy"] = [2, 3, 1, 5, 4]
spotify_orderings["acousticness"] = [4, 1, 5, 2, 3]
spotify_orderings["speechiness"] = [1, 4, 5, 2, 3]
spotify_orderings["liveness"] = [1, 3, 5, 2, 4]

survey_orderings = []

survey_orderings_1 = {}
survey_orderings_1["danceability"] = [4, 2, 3, 5, 1]
survey_orderings_1["valence"] = [3, 4, 2, 5, 1]
survey_orderings_1["energy"] = [2, 3, 4, 5, 1]
survey_orderings_1["acousticness"] = [1, 4, 5, 2, 3]
survey_orderings_1["speechiness"] = [1, 3, 5, 2, 4]
survey_orderings_1["liveness"] = [3, 1, 5, 2, 4]
survey_orderings.append(survey_orderings_1)

survey_orderings_2 = {}
survey_orderings_2["danceability"] = [4, 3, 2, 5, 1]
survey_orderings_2["valence"] = [4, 2, 5, 1, 3]
survey_orderings_2["energy"] = [2, 3, 5, 1, 4]
survey_orderings_2["acousticness"] = [1, 4, 5, 2, 3]
survey_orderings_2["speechiness"] = [1, 4, 2, 5, 3]
survey_orderings_2["liveness"] = [1, 3, 5, 4, 2]
survey_orderings.append(survey_orderings_2)

survey_orderings_3 = {}
survey_orderings_3["danceability"] = [3, 4, 2, 5, 1]
survey_orderings_3["valence"] = [4, 3, 1, 2, 5]
survey_orderings_3["energy"] = [2, 3, 1, 5, 4]
survey_orderings_3["acousticness"] = [4, 2, 5, 1, 3]
survey_orderings_3["speechiness"] = [1, 4, 2, 3, 5]
survey_orderings_3["liveness"] = [5, 3, 1, 2, 4]
survey_orderings.append(survey_orderings_3)

survey_orderings_4 = {}
survey_orderings_4["danceability"] = [3, 4, 2, 5, 1]
survey_orderings_4["valence"] = [4, 3, 2, 1, 5]
survey_orderings_4["energy"] = [2, 3, 1, 5, 4]
survey_orderings_4["acousticness"] = [4, 1, 5, 2, 3]
survey_orderings_4["speechiness"] = [1, 4, 5, 2, 3]
survey_orderings_4["liveness"] = [1, 3, 5, 2, 4]
survey_orderings.append(survey_orderings_4)

survey_orderings_5 = {}
survey_orderings_5["danceability"] = [4, 3, 2, 5, 1]
survey_orderings_5["valence"] = [4, 3, 2, 1, 5]
survey_orderings_5["energy"] = [2, 3, 1, 5, 4]
survey_orderings_5["acousticness"] = [4, 5, 1, 2, 3]
survey_orderings_5["speechiness"] = [1, 4, 5, 2, 3]
survey_orderings_5["liveness"] = [1, 3, 5, 2, 4]
survey_orderings.append(survey_orderings_5)

survey_orderings_6 = {}
survey_orderings_6["danceability"] = [4, 3, 2, 5, 1]
survey_orderings_6["valence"] = [4, 1, 2, 3, 5]
survey_orderings_6["energy"] = [1, 2, 3, 5, 4]
survey_orderings_6["acousticness"] = [5, 1, 4, 2, 3]
survey_orderings_6["speechiness"] = [1, 4, 5, 2, 3]
survey_orderings_6["liveness"] = [1, 5, 3, 2, 4]
survey_orderings.append(survey_orderings_6)

survey_orderings_7 = {}
survey_orderings_7["danceability"] = [4, 3, 5, 2, 1]
survey_orderings_7["valence"] = [4, 3, 2, 1, 5]
survey_orderings_7["energy"] = [2, 3, 1, 5, 4]
survey_orderings_7["acousticness"] = [4, 1, 5, 2, 3]
survey_orderings_7["speechiness"] = [1, 4, 5, 2, 3]
survey_orderings_7["liveness"] = [1, 3, 2, 5, 4]
survey_orderings.append(survey_orderings_7)

survey_orderings_8 = {}
survey_orderings_8["danceability"] = [4, 3, 5, 2, 1]
survey_orderings_8["valence"] = [4, 3, 2, 5, 1]
survey_orderings_8["energy"] = [2, 5, 1, 3, 4]
survey_orderings_8["acousticness"] = [4, 1, 5, 2, 3]
survey_orderings_8["speechiness"] = [4, 1, 5, 2, 3]
survey_orderings_8["liveness"] = [1, 3, 2, 5, 4]
survey_orderings.append(survey_orderings_8)

survey_orderings_9 = {}
survey_orderings_9["danceability"] = [4, 2, 3, 5, 1]
survey_orderings_9["valence"] = [4, 3, 2, 1, 5]
survey_orderings_9["energy"] = [3, 2, 1, 5, 4]
survey_orderings_9["acousticness"] = [4, 1, 5, 3, 2]
survey_orderings_9["speechiness"] = [1, 4, 2, 5, 3]
survey_orderings_9["liveness"] = [3, 1, 5, 2, 4]
survey_orderings.append(survey_orderings_9)

survey_orderings_10 = {}
survey_orderings_10["danceability"] = [4, 3, 2, 5, 1]
survey_orderings_10["valence"] = [4, 3, 2, 1, 5]
survey_orderings_10["energy"] = [2, 3, 1, 5, 4]
survey_orderings_10["acousticness"] = [4, 2, 5, 1, 3]
survey_orderings_10["speechiness"] = [1, 4, 5, 2, 3]
survey_orderings_10["liveness"] = [1, 3, 5, 2, 4]
survey_orderings.append(survey_orderings_10)

scores = {"danceability":0, "valence":0, "energy":0, "acousticness":0, "speechiness":0, "liveness":0}

# Penalizes further distance heavier
def computeMeanSquared(survey_feature_ordering, feature):
	score = 0
	for spotify_index, track in enumerate(spotify_orderings[feature]):
		survey_index = survey_feature_ordering.index(track)
		score += (spotify_index - survey_index)**2
	score /= num_tracks
	return score

def getScore():
	for ordering in survey_orderings:
		for feature in ordering:
			scores[feature] += computeMeanSquared(ordering[feature], feature)
	for feature in scores:
		scores[feature] /= num_surveys
	print scores

if __name__ == '__main__':
	getScore()
