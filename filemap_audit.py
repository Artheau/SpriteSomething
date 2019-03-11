import argparse
import os
import struct
import csv
import numpy as np
from PIL import Image

from constants import *

rom = None
filemap = None



def load_filemap(filename='resources/filemap.csv'):
    filemap = {}
    with open(filename, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        next(spamreader)             #skip header
        for row in spamreader:
            animation_number = int(row[0])
            pose_number = int(row[2])
            timeline_number = int(row[3])
            upper_map = row[4]
            upper_file = row[5]
            upper_palette = row[6]
            lower_map = row[7]
            lower_file = row[8]
            lower_palette = row[9]

            filemap[(animation_number,timeline_number)] = { 'pose_number': pose_number,
                                                        'upper_map': upper_map,
                                                        'upper_file': upper_file,
                                                        'upper_palette': upper_palette,
                                                        'lower_map': lower_map,
                                                        'lower_file': lower_file,
                                                        'lower_palette': lower_palette}
    return filemap


def main():
    global filemap

    filemap = load_filemap()

    upper_set = set([data['upper_file'] for data in filemap.values()])
    lower_set = set([data['lower_file'] for data in filemap.values()])

    upper_appears_with = {}
    lower_appears_with = {}
    for key in filemap:
        if filemap[key]['upper_file'] in upper_appears_with:
            upper_appears_with[filemap[key]['upper_file']].add(filemap[key]['lower_file'])
        else:
            upper_appears_with[filemap[key]['upper_file']] = set([filemap[key]['lower_file']])
        if filemap[key]['lower_file'] in lower_appears_with:
            lower_appears_with[filemap[key]['lower_file']].add(filemap[key]['upper_file'])
        else:
            lower_appears_with[filemap[key]['lower_file']] = set([filemap[key]['upper_file']])

    clean_upper_appears_with = {}
    for key in upper_appears_with:
        if len(upper_appears_with[key]) > 1:
            clean_upper_appears_with[key] = upper_appears_with[key]
            #print(f"{key}: {upper_appears_with[key]}")
    clean_lower_appears_with = {}
    for key in lower_appears_with:
        if len(lower_appears_with[key]) > 1:
            clean_lower_appears_with[key] = lower_appears_with[key]
            print(f"{key}: {lower_appears_with[key]}")


    

if __name__ == "__main__":
    main()

