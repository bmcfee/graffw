#!/usr/bin/env python

import numpy as np
import cPickle as pickle
import ujson as json
import os
import glob

#-- collection functions
#-- track functions
def get_track_audio(track_id):
    
    track = json.load(open('data/%08d.json' % track_id))

    return track['recording_id']


def get_track_analysis(track_id):

    analysis = json.load(open('data/%08d.json' % track_id))
    analysis['recording_id'] = track_id

    return analysis
