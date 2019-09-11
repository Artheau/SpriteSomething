#!/bin/bash

set -ev

#make dir to put app icon in
mkdir -p "../pages/app_resources/meta/icons/"
#copy icon over
cp "./app_resources/meta/icons/app.gif" "../pages/app_resources/meta/icons/"
#make dir to put build version in
mkdir -p "../pages/app_resources/meta/manifests/"
mv "../build/app_version.txt" "../pages/app_resources/meta/manifests/app_version.txt"

#copy GitHub pages files to staging area
mv "./pages_resources/index.html" "../pages/"						#move index page that lists version number
cp -rf "./pages_resources" "../pages/app_resources/"	#copy sprite preview pages
ls -l "./app_resources" | grep "^d" | grep -o "\S*$" | sed "meta/d" > "../build/games.txt" #get list of games
cp -f "../build/games.txt" "../pages/app_resources/meta/manifests/" #copy list of games
#copy game manifests over
for game in $(cat "../build/games.txt"); \
  do mkdir -p "../pages/app_resources/$game/manifests/"; \
	cp "./app_resources/$game/manifests/*" $_; \
	mkdir -p "../pages/app_resources/$game/lang/"; \
	cp "./app_resources/$game/lang/*" $_; \
done

#nuke GitHub pages files from source code
rm -rf "./pages_resources"

#set pages to upload
PAGES="../pages"

echo "GHPages Staging: ${PAGES}"
