#!/bin/sh

set -eu

# Check if arguments provided
if [ $# -eq 0 ]
then
	# If argument NOT provided, let Discord show the event informations.

	echo Sending event informations

	if [ $DISCORD_BODY -ne ""]
	then
		echo Specified Payload

		curl -X POST -H "Content-Type: application/json" --data "$DISCORD_BODY" $DISCORD_WEBHOOK
	else
		echo Payload : $(cat $GITHUB_EVENT_PATH)

		curl -X POST -H "Content-Type: application/json" --data "$(cat $GITHUB_EVENT_PATH)" $DISCORD_WEBHOOK/github
	fi

else
	# If argument provided, override the Discord message.

	echo Sending : $*

	#curl -X POST -H "Content-Type: application/json" --data "{ \"content\": \"$*\" }" $DISCORD_WEBHOOK
	curl -X POST -H "Content-Type: application/json" --data "$(cat $*)" $DISCORD_WEBHOOK
fi
