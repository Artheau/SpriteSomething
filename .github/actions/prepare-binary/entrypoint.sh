#!/bin/bash

set -ev

#make dir to put metadata in
mkdir "../build"

#jot down a note of the files in the dir
ls -p > "../build/filename.txt"
chmod 775 "../build/filename.txt"
#use my pcregrep script to list binaries
python ./source/fakepcregrep.py

echo "Binary Listing"
cat "../build/filename.txt"
echo " "

mkdir "../artifact"
echo "example binary" > "../artifact/example.txt"
