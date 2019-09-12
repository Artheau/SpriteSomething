#!/bin/bash

set -ev

# move filename note from artifact download
mkdir "../build"
mv "filename.txt" "../build/filename.txt"

# update app version with build number
APP_VERSION=$(head -n 1 "./app_resources/meta/manifests/app_version.txt")
export GITHUB_TAG="${APP_VERSION}.${GITHUB_SHA:0:7}"
echo "${GITHUB_TAG}" > "./app_resources/meta/manifests/app_version.txt"

#make dir to put archive/binary in
mkdir "../deploy"

#chmod user_resources for working_dirs.json
chmod 775 "./user_resources"
chmod 775 "./user_resources/meta"
chmod 775 "./user_resources/meta/manifests"

#get the first listing
BUILD_FILENAME=$(head -n 1 "../build/filename.txt")
chmod +x ${BUILD_FILENAME}

# if we've got a filename
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
	DIST_NAME="notset"
	#extrapolate ubuntu distribution name
	if [[ "$OS_NAME" =~ "ubuntu" ]]; then
		VER_TEST="latest"
		if [[ "$OS_NAME" =~ "$VER_TEST" ]]; then
			DIST_NAME="bionic"
			OS_NAME="${OS_NAME/-$VER_TEST/}"
		fi

		VER_TEST="16.04"
		if [[ "$OS_NAME" =~ "$VER_TEST" ]]; then
			DIST_NAME="xenial"
			OS_NAME="${OS_NAME/-$VER_TEST/}"
		fi
		OS_NAME="ubuntu"
	fi
	OS_NAME="${OS_NAME/-latest/}"
	DEST_SLUG="${DEST_SLUG}-${GITHUB_TAG}-${OS_NAME}"

	if [ "${DIST_NAME}" != "" ] && [ "${DIST_NAME}" != "notset" ]; then
		DEST_SLUG="${DEST_SLUG}-${DIST_NAME}"
	fi
	DEST_FILENAME="${DEST_SLUG}${DEST_EXTENSION}"

	#move binary to a temp folder
	mv $BUILD_FILENAME "../build/${DEST_FILENAME}"

	#clean the git slate but don't clobber stuff if we're running this locally
	git clean -dfx --exclude=.vscode --exclude=.idea --exclude=*.json

	#move the binary back
	mv "../build/${DEST_FILENAME}" "./${DEST_FILENAME}"

	#set release name
	#set files to upload
	#now that we have the tag sorted, set it in git
	export GITHUB_TAG="v${GITHUB_TAG}"
	export RELEASE_NAME="SpriteSomething ${GITHUB_TAG}"
	FILES="../deploy/*"
	git tag ${GITHUB_TAG}

	if [[ "${OS_NAME}" != "" ]]; then
		rm -rf ./.git
	fi

	if [ "${OS_NAME}" == "windows" ]; then
		#windows uses archiver
		#jot down a note of what the filename is
		#use my pcregrep script to list binaries
		#move the zip to the deployment folder
		ZIP_FILENAME="${DEST_SLUG}.zip"
		arc archive "../${ZIP_FILENAME}" "./"
		mv "../${ZIP_FILENAME}" "../deploy/${ZIP_FILENAME}"
		echo "../deploy/${ZIP_FILENAME}" > "../build/filename.txt" #deploy archive
		python "./source/fakepcregrep.py"
	else
		#we're using tar
		#move the zip to the deployment folder
		ZIP_FILENAME="${DEST_SLUG}.tar.gz"
		tar -czf "../${ZIP_FILENAME}" "./"
		mv "../${ZIP_FILENAME}" "../deploy/${ZIP_FILENAME}"
	fi

	#print summary of info
	#filename of initial binary
	#filename of final binary
	#filename of archive
	#filesize of binary
	#filesize or archive
	echo "Build Filename: ${BUILD_FILENAME}"
	echo "Dest Filename:  ${DEST_FILENAME}"
	echo "Zip Filename:   ../deploy/${ZIP_FILENAME}"

	if [ "${OS_NAME}" != "macOS" ]; then
		#macosx does this weird
		#the rest are standardized
		FILESIZE=$(ls -lh ${DEST_FILENAME} | cut -d " " -f 5)
		ZIPSIZE=$(ls -lh "../deploy/${ZIP_FILENAME}" | cut -d " " -f 5)
		echo "Build Filesize: ${FILESIZE}"
		echo "Zip Filesize:   ${ZIPSIZE}"
	fi

fi

#echo "Deploy:         ${DEPLOY}"
#echo "Deploy Pages:   ${DEPLOY_PAGES}"
echo "Files to Upload: ${FILES}"
echo "Release Name:    ${RELEASE_NAME}"
echo "Git tag:         ${GITHUB_TAG}"
