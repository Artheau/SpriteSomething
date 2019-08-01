#!/bin/bash

set -ev

#list binaries
ls -p | pcregrep -M ${REGEX}

#save list
BUILD_FILENAME=$(ls -p | pcregrep -M ${REGEX})

#if we've got a filename
if [ "${BUILD_FILENAME}" != "" ]; then
	#if the filename is the same without a period
	if [ "${BUILD_FILENAME/.}" == "${BUILD_FILENAME}" ]; then
		#we've got no extension
		#it's a linux or mac build
		DEST_EXTENSION=""
	else
		#we've got an extension, save it (with a prepended period) and the filename portion
		DEST_EXTENSION=".${BUILD_FILENAME##*.}"
		BUILD_FILENAME="${BUILD_FILENAME%.*}"
	fi

	#build the filename
	#current: <build_filename>-<git_tag>-<os_name>-<linux_distro><file_extension>
	DEST_FILENAME="${BUILD_FILENAME}-${TRAVIS_TAG}-${TRAVIS_OS_NAME}"
	if [ "${TRAVIS_DIST}" != "" ] && [ "${TRAVIS_DIST}" != "notset" ]; then
		DEST_FILENAME="${DEST_FILENAME}-${TRAVIS_DIST}"
	fi
	DEST_FILENAME="${DEST_FILENAME}${DEST_EXTENSION}"
	echo "Build Filename: ${BUILD_FILENAME}"
	echo "Dest Filename:  ${DEST_FILENAME}"

	mv $BUILD_FILENAME $DEST_FILENAME

	FILESIZE=$(ls -lh ${DEST_FILENAME} | cut -d " " -f 5)
	echo "Filesize:       ${FILESIZE}"
fi
