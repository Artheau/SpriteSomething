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
	wget --output-document=${UPX_FILE} ${UPX_URL}

	#use archiver that we installed before getting here
	arc unarchive ${UPX_FILE} $HOME/upx

	#move upx to where pyinstaller expects it to be
	mv $HOME/upx/${UPX_SLUG}/* $HOME/${TRAVIS_REPO_SLUG}/upx
	echo "Moved UPX"

	ls -p $HOME/${TRAVIS_REPO_SLUG}/upx
else
	curl -L ${UPX_URL} --output ${UPX_FILE}
	tar -C $HOME/upx -xf ${UPX_FILE}

	#move upx to where pyinstaller expects it to be
	mv $HOME/upx/${UPX_SLUG}/* $HOME/${TRAVIS_REPO_SLUG}/upx
	echo "Moved UPX"

	ls -p $HOME/${TRAVIS_REPO_SLUG}/upx
fi
