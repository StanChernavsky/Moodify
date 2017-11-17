#!/usr/bin/python

import random
import collections
import math
import sys
from util import *

############################################################
# Problem 3: binary classification
############################################################

############################################################
# Problem 3a: feature extraction

def extractWordFeatures(x):
    """
    Extract word features for a string x. Words are delimited by
    whitespace characters only.
    @param string x: 
    @return dict: feature vector representation of x.
    Example: "I am what I am" --> {'I': 2, 'am': 2, 'what': 1}
    """
    # BEGIN_YOUR_CODE (our solution is 4 lines of code, but don't worry if you deviate from this)
    return dict(Counter(x.split()))
    # END_YOUR_CODE
############################################################
# Problem 3b: stochastic gradient descent

def learnPredictor(trainExamples, testExamples, featureExtractor, numIters, eta):
    '''
    Given |trainExamples| and |testExamples| (each one is a list of (x,y)
    pairs), a |featureExtractor| to apply to x, and the number of iterations to
    train |numIters|, the step size |eta|, return the weight vector (sparse
    feature vector) learned.

    You should implement stochastic gradient descent.

    Note: only use the trainExamples for training!
    You should call evaluatePredictor() on both trainExamples and testExamples
    to see how you're doing as you learn after each iteration.
    '''
    weights = {}  # feature => weight
    # BEGIN_YOUR_CODE (our solution is 12 lines of code, but don't worry if you deviate from this)
    def predictor(x):
        prediction = 1 if dotProduct(weights, featureExtractor(x)) >= 0 else -1
        return prediction
        
    for i in xrange(numIters):
        for x,y in trainExamples:
            extractedFeaturesX = featureExtractor(x)
            margin = y*dotProduct(weights, extractedFeaturesX)
            if margin >= 1:
                continue
            increment(weights, eta*y, extractedFeaturesX)
        print "train: %.5f | test: %.5f" % (evaluatePredictor(trainExamples, predictor), evaluatePredictor(testExamples, predictor))
    # END_YOUR_CODE
    return weights


############################################################
# Problem 3c: generate test case

def generateDataset(numExamples, weights):
    '''
    Return a set of examples (phi(x), y) randomly which are classified correctly by
    |weights|.
    '''
    random.seed(42)
    # Return a single example (phi(x), y).
    # phi(x) should be a dict whose keys are a subset of the keys in weights
    # and values can be anything (randomize!) with a nonzero score under the given weight vector.
    # y should be 1 or -1 as classified by the weight vector.
    def generateExample():
        # BEGIN_YOUR_CODE (our solution is 2 lines of code, but don't worry if you deviate from this)
        subset = random.sample(weights.items(), random.randint(1, len(weights.keys())))
        phi = {key: random.uniform(-0.4, 0.4) for key, val in subset}
        y = 1 if dotProduct(phi, weights) >= 0 else -1
        # END_YOUR_CODE
        return (phi, y)
    return [generateExample() for _ in range(numExamples)]

############################################################
# Problem 3e: character features

def extractCharacterFeatures(n):
    '''
    Return a function that takes a string |x| and returns a sparse feature
    vector consisting of all n-grams of |x| without spaces.
    EXAMPLE: (n = 3) "I like tacos" --> {'Ili': 1, 'lik': 1, 'ike': 1, ...
    You may assume that n >= 1.
    '''
    def extract(x):
        # BEGIN_YOUR_CODE (our solution is 6 lines of code, but don't worry if you deviate from this)
        whitespaceRemoved = ''.join(x.split())
        strings = [whitespaceRemoved[i:i+n] for i in xrange(len(whitespaceRemoved)-n+1)]
        return dict(Counter(strings))
        # END_YOUR_CODE
    return extract

############################################################
# Problem 4: k-means
############################################################


def kmeans(examples, K, maxIters):
    '''
    examples: list of examples, each example is a string-to-double dict representing a sparse vector.
    K: number of desired clusters. Assume that 0 < K <= |examples|.
    maxIters: maximum number of iterations to run (you should terminate early if the algorithm converges).
    Return: (length K list of cluster centroids,
            list of assignments (i.e. if examples[i] belongs to centers[j], then assignments[i] = j)
            final reconstruction loss)
    '''
    # BEGIN_YOUR_CODE (our solution is 32 lines of code, but don't worry if you deviate from this)
    def initializeCenters(K):
        return random.sample(examples, K)
        
    def assignCentroid(coord, centers, idx):
        minDistance = computeDistanceOptimized(coord, centers[0], xSquared[idx], muSquared[0])
        closestCentroidIdx = 0
        for i in xrange(K):
            distance = computeDistanceOptimized(coord, centers[i], xSquared[idx], muSquared[i]) #(coord - centers[i])**2
            if distance < minDistance:
                minDistance = distance
                closestCentroidIdx = i
        return (closestCentroidIdx, minDistance)
    
    def computeAverage(center):
        sumVector = {item: 0 for item, val in center.items()}
        count = 0
        for idx in xrange(len(assignments)):
            if assignments[idx] == center:
                increment(sumVector, 1, examples[idx])
                count += 1
        if count == 0:
            return center
        else:
            return {key: (1.0/count)*value for key, value in sumVector.items()}
    
    def computeDistanceOptimized(coord, center, xSquaredVal, muSquaredVal):
        return abs(xSquaredVal + muSquaredVal - 2*dotProduct(coord, center))
        
    assignments = {}
    centers = initializeCenters(K)
    muSquared = [dotProduct(center, center) for center in centers]
    xSquared = [dotProduct(example, example) for example in examples]
    finalReconstructionLoss = 0
    prevFRL = 1
    
    
    for iterIdx in xrange(maxIters):
        if prevFRL == finalReconstructionLoss:
            break
        
        prevFRL = finalReconstructionLoss
        finalReconstructionLoss = 0
        averages = {i: [0, {item: 0 for item, val in centers[0].items()}] for i in xrange(K)}
        # Step 1
        for e in xrange(len(examples)):
            coord = examples[e]
            closestCentroidIdx, distance = assignCentroid(coord, centers, e)
            assignments[e] = closestCentroidIdx
            increment(averages[closestCentroidIdx][1], 1, examples[e])
            averages[closestCentroidIdx][0] += 1
            finalReconstructionLoss += distance
            
        # Step 2
        for c in xrange(K):
            if averages[c][0] == 0:
                continue
            else:
                centers[c] = {key: (1.0/averages[c][0]) * value for key, value in averages[c][1].items()}
        muSquared = [dotProduct(center, center) for center in centers]
        
    return centers, assignments, finalReconstructionLoss
    # END_YOUR_CODE