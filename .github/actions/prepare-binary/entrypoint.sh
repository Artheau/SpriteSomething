#!/bin/bash

set -ev

#make dir to put metadata in
mkdir "../build"
#make dir to put artifact in
mkdir "../artifact"

#jot down a note of the files in the dir
ls -p > "../build/filename.txt"
chmod 775 "../build/filename.txt"
#use my pcregrep script to list binaries
python ./source/fakepcregrep.py

#get binary filename
BUILD_FILENAME=$(head -n 1 "../build/filename.txt")

#copy binary filename & binary itself to artifact staging
cp BUILD_FILENAME "../artifact"
cp "../build/filename.txt" "../artifact"
