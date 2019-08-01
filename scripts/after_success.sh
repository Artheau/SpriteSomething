#!/bin/bash

set -ev

if [ "${TRAVIS_OS_NAME}" == "windows" ]; then
	ls -p > "./build/SpriteSomething/filename.txt"
	${PYTHON_EXECUTABLE} ./source/fakepcregrep.py
	BUILD_FILENAME=$(head -n 1 ./build/SpriteSomething/filename.txt)
	rm "./build/SpriteSomething/filename.txt"
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

	FILESIZE_DELIM = " "
	if [ "${TRAVIS_OS_NAME}" == "osx" ]; then
		FILESIZE_DELIM = "\t"
	fi
	FILESIZE=$(ls -lh ${DEST_FILENAME} | cut -d ${FILESIZE_DELIM} -f 5)
	echo "Filesize:       ${FILESIZE}"
fi
