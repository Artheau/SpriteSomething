#!/bin/bash

set -ev

#make dir to put the archive/binary in
mkdir ../deploy
#make dir to put some build metadata in
mkdir ../build
#make dir to put build version in
mkdir -p ../pages/app_resources/meta/manifests/
echo "${TRAVIS_TAG}" > "../pages/app_resources/meta/manifests/app_version.txt"

#chmod user_resources to hopefully fix working_dirs.json issue
chmod 775 "./user_resources"
chmod 775 "./user_resources/meta"
chmod 775 "./user_resources/meta/manifests"

#copy GitHub pages files to staging area
mv ./pages_resources/index.html ../pages/						#move index page that lists version number
cp -rf ./pages_resources/* ../pages/app_resources/	#copy sprite preview pages
ls -l ./app_resources | grep "^d" | grep -o "\S*$" | sed '/meta/d' > "../build/games.txt"	#get list of games
cp -f ../build/games.txt ../pages/app_resources/meta/manifests/		#copy list of games
# copy game manifests over
for game in $(cat ../build/games.txt); \
do mkdir -p ../pages/app_resources/$game/manifests/; \
cp ./app_resources/$game/manifests/* $_; \
mkdir -p ../pages/app_resources/$game/lang/; \
cp ./app_resources/$game/lang/* $_; \
done

#nuke GitHub pages files from source code
rm -rf ./pages_resources

#if we're on windows, jot down a note of the files in the dir
if [ "${TRAVIS_OS_NAME}" == "windows" ]; then
	ls -p > "../build/filename.txt"
	chmod 775 "../build/filename.txt"
	#use my pcregrep script to list binaries
	${PYTHON_EXECUTABLE} ./source/fakepcregrep.py
	#get the first listing
	BUILD_FILENAME=$(head -n 1 ../build/filename.txt)
else
	#list binaries
	ls -p | pcregrep -M ${REGEX}

	#save list
	BUILD_FILENAME=$(ls -p | pcregrep -M ${REGEX})
fi

#if we've got a filename
if [ "${BUILD_FILENAME}" != "" ]; then
	#if the filename is the same without a period
	if [ "${BUILD_FILENAME/.}" == "${BUILD_FILENAME}" ]; then
		#we've got no extension
		#it's a linux or mac build
		DEST_EXTENSION=""
		DEST_SLUG="${BUILD_FILENAME}"
	else
		#we've got an extension, save it (with a prepended period) and the filename portion
		DEST_EXTENSION=".${BUILD_FILENAME##*.}"
		DEST_SLUG="${BUILD_FILENAME%.*}"
	fi

	#build the filename
	#current: <build_filename>-<git_tag>-<os_name>-<linux_distro><file_extension>
	DEST_SLUG="${DEST_SLUG}-${TRAVIS_TAG}-${TRAVIS_OS_NAME}"
	if [ "${TRAVIS_DIST}" != "" ] && [ "${TRAVIS_DIST}" != "notset" ]; then
		DEST_SLUG="${DEST_SLUG}-${TRAVIS_DIST}"
	fi
	DEST_FILENAME="${DEST_SLUG}${DEST_EXTENSION}"

	#move binary to a temp folder
	mv $BUILD_FILENAME ../build/$DEST_FILENAME

	#clean the git slate but don't clobber stuff if we're running this locally
	git clean -dfx --exclude=.vscode --exclude=*.json

	#move the binary back
	mv ../build/$DEST_FILENAME ./$DEST_FILENAME

	if [ "${TRAVIS_OS_NAME}" == "windows" ]; then
		#windows uses archiver
		#jot down a note of what the filename is
		#use my pcregrep script to list binaries
		#move the zip to deployment folder
		ZIP_FILENAME="${DEST_SLUG}.zip"
		arc archive ../${ZIP_FILENAME} ./
		mv ../${ZIP_FILENAME} ../deploy/${ZIP_FILENAME}
		#echo ${DEST_FILENAME} > "../build/filename.txt"	#deploy binary
		echo "../deploy/${ZIP_FILENAME}" > "../build/filename.txt"	#deploy archive
		${PYTHON_EXECUTABLE} ./source/fakepcregrep.py
	else
		#else, we're using tar
		#move the zip to deployment folder
		ZIP_FILENAME="${DEST_SLUG}.tar.gz"
		tar -czf ../${ZIP_FILENAME} ./
		mv ../${ZIP_FILENAME} ../deploy/${ZIP_FILENAME}
	fi

	#print summary of info
	#filename of initial binary
	#filename of final binary
	#filename of archive
	#filesize of binary
	#filesize of archive
	# sometimes the archive is super huger than the binary, and that's weird; trying to understand it a bit more
	echo "Build Filename: ${BUILD_FILENAME}"
	echo "Dest Filename:  ${DEST_FILENAME}"
	echo "Zip Filename:   ../deploy/${ZIP_FILENAME}"
	if [ "${TRAVIS_OS_NAME}" == "osx" ]; then
		#macosx does this weird, gotta use the native delimiter and capture it
		FILESIZE=$(ls -lh ${DEST_FILENAME} | pcregrep -M -o4 "^([-[:alpha:]\s]*)(\d*)([[:alpha:]\s]*)(\S*)(.*)$")
		ZIPSIZE=$(ls -lh ../deploy/${ZIP_FILENAME} | pcregrep -M -o4 "^([-[:alpha:]\s]*)(\d*)([[:alpha:]\s]*)(\S*)(.*)$")
	else
		#the rest are standardized
		FILESIZE=$(ls -lh ${DEST_FILENAME} | cut -d " " -f 5)
		ZIPSIZE=$(ls -lh ../deploy/${ZIP_FILENAME} | cut -d " " -f 5)
	fi
	echo "Build Filesize: ${FILESIZE}"
	echo "Zip Filesize:   ${ZIPSIZE}"
fi
