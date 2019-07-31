#!/bin/bash

set -ev

#list binaries
ls -p | grep -E '^(.\/)?([[:alnum:]-])*(.exe|$)'

#save list
export BUILD_FILENAME=$(ls -p | grep -E '^(.\/)?([[:alnum:]-])*(.exe|$)')

#if no tag was submitted, let's build one
if [ "${TRAVIS_TAG}" == "" ]; then
	#current: default to build number (a 3-digit number at this time above 150)
	#future:  <major>.<minor>.<build_number>,
	# to be read from a text file that's in the repo with the intended <major>.<minor> version numbers
	# FIXME: Do that
	export TRAVIS_TAG="${TRAVIS_BUILD_NUMBER}"
fi

#if we've got a filename
if [ "${BUILD_FILENAME}" != "" ]; then
	#if the filename is the same without a period
	if [ "${BUILD_FILENAME/.}" == "${BUILD_FILENAME}" ]; then
		#we've got no extension
		#it's a linux or mac build
		export DEST_EXTENSION=""
	else
		#we've got an extension, save it (with a prepended period) and the filename portion
		export DEST_EXTENSION=".${BUILD_FILENAME##*.}"
    export BUILD_FILENAME="${BUILD_FILENAME%.*}"
	fi

	#build the filename
	#current: <build_filename>-<git_tag>-<os_name><file_extension>
	#future:  <build_filename>-<git_tag>-<os_name>-<linux_distro><file_extension>
	#FIXME: Do that
	export DEST_FILENAME="${BUILD_FILENAME}-${TRAVIS_TAG}-${TRAVIS_OS_NAME}${DEST_EXTENSION}"
	echo "Build Filename: ${BUILD_FILENAME}"
  echo "Dest Filename:  ${DEST_FILENAME}"
  mv $BUILD_FILENAME $DEST_FILENAME
fi

#list binaries
ls -p | grep -E '^(.\/)?([[:alnum:]-])*(.exe|$)'
#save list
export FILES_TO_UPLOAD=$(ls -p | grep -E '^(.\/)?([[:alnum:]-])*(.exe|$)')
#output final deployment info
echo "Deploy: ${DEPLOY}"
echo "Files to Upload: ${FILES_TO_UPLOAD}"
echo "Git tag: ${TRAVIS_TAG}
