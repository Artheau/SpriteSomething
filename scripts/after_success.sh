#!/bin/bash

set -ev

if [ "${TRAVIS_OS_NAME}" == "windows" ]; then
	ls -p > "./build/SpriteSomething/filename.txt"
	${PYTHON_EXECUTABLE} ./source/fakepcregrep.py
	BUILD_FILENAME=$(head -n 1 ./build/SpriteSomething/filename.txt)
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

	mv $BUILD_FILENAME $DEST_FILENAME

	EXCLUDES="--exclude=./__pycache__ --exclude=./build "
	if [ "${TRAVIS_OS_NAME}" == "windows" ]; then
		ZIP_FILENAME="${DEST_SLUG}.zip"
		arc archive ../${ZIP_FILENAME} ./ --exclude=./__pycache__/ --exclude=./build/
		mkdir ./archive
		mv ../${ZIP_FILENAME} ./archive/${ZIP_FILENAME}
		echo "./archive/${ZIP_FILENAME}" > "./build/SpriteSomething/filename.txt"
		${PYTHON_EXECUTABLE} ./source/fakepcregrep.py
	else
		if [ "${TRAVIS_OS_NAME}" == "osx" ]; then
			EXCLUDES=""
		fi
		ZIP_FILENAME="${DEST_SLUG}.tar.gz"
		tar -czf ../${ZIP_FILENAME} ./ ${EXCLUDES}
		mkdir ./archive
		mv ../${ZIP_FILENAME} ./archive/${ZIP_FILENAME}
	fi

	echo "Build Filename: ${BUILD_FILENAME}"
	echo "Dest Filename:  ${DEST_FILENAME}"
	echo "Zip Filename:   ./archive/${ZIP_FILENAME}"
	if [ "${TRAVIS_OS_NAME}" == "osx" ]; then
		FILESIZE=$(ls -lh ${DEST_FILENAME} | pcregrep -M -o4 "^([-[:alpha:]\s]*)(\d*)([[:alpha:]\s]*)(\S*)(.*)$")
		ZIPSIZE=$(ls -lh ./archive/${ZIP_FILENAME} | pcregrep -M -o4 "^([-[:alpha:]\s]*)(\d*)([[:alpha:]\s]*)(\S*)(.*)$")
	else
		FILESIZE=$(ls -lh ${DEST_FILENAME} | cut -d " " -f 5)
		ZIPSIZE=$(ls -lh ./archive/${ZIP_FILENAME} | cut -d " " -f 5)
	fi
	echo "Build Filesize: ${FILESIZE}"
	echo "Zip Filesize:   ${ZIPSIZE}"
fi
