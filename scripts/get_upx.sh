#!/bin/bash

set -ev

#set up download url
UPX_SLUG=upx-${UPX_VERSION}-amd64_linux
UPX_FILE=${UPX_SLUG}.tar.xz
UPX_URL=https://github.com/upx/upx/releases/download/v${UPX_VERSION}/${UPX_FILE}

#make some dirs
mkdir -p $HOME/upx
mkdir -p $HOME/${TRAVIS_REPO_SLUG}/upx

#different archiving utilities
if [ "${TRAVIS_OS_NAME}" == "windows" ]; then
	#curl seems to fail on windows builds
	echo "Getting UPX"
	wget --output-document=${UPX_FILE} ${UPX_URL}
	echo "Got UPX"

	#use archiver that we installed before getting here
	echo "Extracting UPX"
	arc unarchive ${UPX_FILE} $HOME/upx
	echo "Extracted UPX"

	#move upx to where pyinstaller expects it to be
	echo "Moving UPX"
	mv $HOME/upx/${UPX_SLUG}/* $HOME/${TRAVIS_REPO_SLUG}/upx
	echo "Moved UPX"

	#delete the folder we extracted it to initially
	rm -r $HOME/upx

	ls $HOME/${TRAVIS_REPO_SLUG}/upx
else
	echo "Getting UPX"
	curl -L ${UPX_URL} --output ${UPX_FILE}
	echo "Got UPX"

	echo "Extracting UPX"
	tar -C $HOME/upx -xf ${UPX_FILE}
	echo "Extracted UPX"

	#move upx to where pyinstaller expects it to be
	echo "Moving UPX"
	mv $HOME/upx/${UPX_SLUG}/* $HOME/${TRAVIS_REPO_SLUG}/upx
	echo "Moved UPX"

	#delete the folder we extracted it to initially
	rm -r $HOME/upx

	ls $HOME/${TRAVIS_REPO_SLUG}/upx
fi
