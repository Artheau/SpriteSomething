#!/bin/bash

set -ev

#set up download url
export UPX_SLUG=upx-${UPX_VERSION}-amd64_linux
export UPX_FILE=${UPX_SLUG}.tar.xz
export UPX_URL=https://github.com/upx/upx/releases/download/v${UPX_VERSION}/${UPX_FILE}

#make some dirs
mkdir -p $HOME/upx
mkdir -p $HOME/${TRAVIS_REPO_SLUG}/upx

#different archiving utilities
if [ "${TRAVIS_OS_NAME}" == "windows" ]; then
	#curl seems to fail on windows builds
	wget --output-document=${UPX_FILE} ${UPX_URL}
	#use archiver that we installed before getting here
  arc unarchive *.tar.xz $HOME/upx
else
	curl -L ${UPX_URL} --output ${UPX_FILE}
  tar -C $HOME/upx -xf *.tar.xz
fi

#move upx to where pyinstaller expects it to be
mv $HOME/upx/${UPX_SLUG}/* $HOME/${TRAVIS_REPO_SLUG}/upx
#delete the folder we extracted it to initially
rm -r $HOME/upx
