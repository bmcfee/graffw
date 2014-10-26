#!/usr/bin/env python
import librosa
import argparse
import sys
import numpy as np
import scipy.sparse

import json as json
from pprint import pprint

def process_arguments(args):

    parser = argparse.ArgumentParser(description='Feature extraction')

    parser.add_argument('input_file', type=str)

    parser.add_argument('output_file', type=str)

    return vars(parser.parse_args(args))


def get_features(infile):
    
    print 'Loading audio'
    y, sr = librosa.load(infile, sr=11025)

    S = librosa.logamplitude(librosa.feature.melspectrogram(y=y, sr=sr, hop_length=256, n_fft=1024))

    onsets = librosa.onset.onset_strength(S=S, sr=sr, hop_length=256)
    print 'Tracking beats'
    tempo, beat_frames = librosa.beat.beat_track(sr=sr, onset_envelope=onsets, hop_length=256, trim=False)

    print 'Extracting MFCC'
    M = librosa.feature.mfcc(S=S, sr=sr)

    Msync = librosa.feature.sync(M, beat_frames)

    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=256)

    return Msync, beat_times


def build_graph(M, rate, alpha=0.5):
    # cost(s,t) = alpha * f(s+1, t) + g(rate, t - s)
    # f(i, j) = ||M[i] - M[j]||^2
    # g(rate, t - s) = (exp(rate) - (t - s))^2
    
    d, n = M.shape

    A = np.zeros((n, n))
    A.fill(np.inf)

    er = np.exp(rate)
    for i in range(n):
        for j in range(i+1, n):
            A[i, j] = np.sum((M[:, i] - M[:, j])**2)
            A[i, j] += alpha * (er - (j-i))**2

    return np.ascontiguousarray(A.T)


def shortest_paths(A):
    
    distances, predecessors = scipy.sparse.csgraph.floyd_warshall(A, return_predecessors=True)

    preds = predecessors[-1]
    preds[-1] = -1

    return list(preds)

def feature_extract(infile, outfile):

    print infile, outfile

    # Get beat-synchronous features
    M, beat_times = get_features(infile)

    # For each rate parameter:
    #   Build the graph
    #   Compute all shortest paths to the final vertex
    #   Store the first hop from each vertex

    obj = {}

    obj['segments'] = [{'time': t, 'duration': d} for (t, d) in zip(beat_times, np.diff(beat_times))]

    obj['speeds'] = [{'id': int(t), 'factor': float(np.exp(t/3.0))} for t in range(1, 4)]

    obj['forward_map'] = {}
    for speed in obj['speeds']:
        print 'Building graph {:d} at rate {:.3f}'.format(speed['id'], speed['factor'])
        A = build_graph(M, speed['factor'])
        
        print 'Computing paths'
        P = shortest_paths(A)
        obj['forward_map'][speed['id']] = [int(z) for z in P]

    with open(outfile, 'w') as f:
        json.dump(obj, f)


if __name__ == '__main__':

    parameters = process_arguments(sys.argv[1:])

    feature_extract(parameters['input_file'], parameters['output_file'])
