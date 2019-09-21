import common
from argparse import ArgumentParser
import datetime
import json
import os
import pytz
import requests

'''
Edit 2
'''

DEFAULT_EVENT = "event"
DEFAULT_REPO_SLUG = "Artheau/SpriteSomething"

colors = {
	"miketrethewey": 0xFFAF00,
	"artheau": 0x344A44,
	"github": 0xFFFFFF
}

env = common.prepare_env()

env["BRANCH"] = os.getenv("TRAVIS_BRANCH","")
env["COMMIT_AUTHOR"] = "GitHub"
env["COMMIT_AVATAR"] = "https://images.discordapp.net/avatars/565119394837954569/f145a84f608c1fb48180bb81a66cf048.png"
env["COMMIT_ID"] = os.getenv("TRAVIS_COMMIT",os.getenv("GITHUB_SHA",""))
env["COMMIT_MESSAGE"] = os.getenv("TRAVIS_COMMIT_MESSAGE","")
env["EVENT_LOG"] = os.getenv("GITHUB_EVENT_PATH","")
env["EVENT_TYPE"] = os.getenv("TRAVIS_EVENT_TYPE",DEFAULT_EVENT)
env["REPO_SLUG"] = os.getenv("TRAVIS_REPO_SLUG",os.getenv("GITHUB_REPOSITORY",DEFAULT_REPO_SLUG))
env["REPO_USERNAME"] = ""
env["REPO_NAME"] = ""
commits = []
query = ""
timestamp = ""

event_manifest = {}
if not env["EVENT_LOG"] == "":
	event_manifest = json.load(open(env["EVENT_LOG"]))

if env["BRANCH"] == "":
	ref = os.getenv("GITHUB_REF","")
	if not ref == "":
		ref = ref.split('/')
		for varname,check in (
			("BRANCH","heads"),
			("TAG","tag")
		):
			if ref[1] == check:
				env[varname] = ref[2]

if "after" in event_manifest:
	if env["COMMIT_ID"] == "":
		env["COMMIT_ID"] = event_manifest["after"]

if env["BRANCH"] == "":
	env["BRANCH"] = "master"

if not env["COMMIT_ID"] == "":
	query = "commit/" + env["COMMIT_ID"]

if "pull" in env["EVENT_TYPE"]:
	env["PULL_ID"] = os.getenv("TRAVIS_PULL_REQUEST","")
	env["PULL_BRANCH"] = os.getenv("TRAVIS_PULL_REQUEST_BRANCH","")
	env["PULL_SHA"] = os.getenv("TRAVIS_PULL_REQUEST_SHA","")
	query = "pull/" + env["PULL_ID"]

if env["COMMIT_MESSAGE"] == "":
	if "commits" in event_manifest:
		if len(event_manifest["commits"]) > 0:
			for commit in event_manifest["commits"]:
				commit_message = commit["message"]
				timestamp = commit["timestamp"]
				if "\n\n" in commit_message:
					commit_parts = commit_message.split("\n\n")
					commit_title = commit_parts.pop(0)
					commit_message = "\n\n".join(commit_parts)
				else:
					commit_title = commit_message
				commit["url"] = commit["url"].replace("***","Artheau")
				commits.append("[`" + commit["id"][:7] + "`](" + commit["url"] + ')' + ' ' + commit_title)
else:
	commit = {}
	commit_message = env["COMMIT_MESSAGE"]
	commit["id"] = env["COMMIT_ID"]
	if "\n\n" in commit_message:
		commit_parts = commit_message.split("\n\n")
		commit_title = commit_parts.pop(0)
		commit_message = "\n\n".join(commit_parts)
	else:
		commit_title = commit_message
	commit["url"] = "http://github.com/" + env["REPO_SLUG"] + '/' + query
	commit["url"] = commit["url"].replace("***","Artheau")
	commits.append("[`" + commit["id"][:7] + "`](" + commit["url"] + ')' + ' ' + commit_title)

if timestamp == "":
	if "repository" in event_manifest:
		if "updated_at" in event_manifest["repository"]:
			timestamp = event_manifest["repository"]["updated_at"]

if timestamp == "":
	utc_now = pytz.utc.localize(datetime.datetime.utcnow())
	pst_now = utc_now.astimezone(pytz.timezone("America/Los_Angeles"))
	timestamp = pst_now.isoformat()
	timestamp = timestamp[:timestamp.find('.')]

if not timestamp == "":
	if '+' in timestamp:
		timestamp = timestamp[:timestamp.find('+')]
	elif '-' in timestamp:
		timestamp = timestamp.split('-')
		_ = timestamp.pop()
		timestamp = '-'.join(timestamp)

if "sender" in event_manifest:
	if "avatar_url" in event_manifest["sender"]:
		env["COMMIT_AVATAR"] = event_manifest["sender"]["avatar_url"]
	if "login" in event_manifest["sender"]:
		env["COMMIT_AUTHOR"] = event_manifest["sender"]["login"]

color = 0x000000
if env["COMMIT_AUTHOR"].lower() in colors:
	color = colors[env["COMMIT_AUTHOR"].lower()]

if len(commits) > 0:
	env["COMMIT_MESSAGE"] = ""
	for commit in commits:
		env["COMMIT_MESSAGE"] += commit + "\n"

if '/' in env["REPO_SLUG"]:
	tmp = env["REPO_SLUG"].split('/')
	env["REPO_USERNAME"] = tmp[0]
	env["REPO_NAME"] = tmp[1]

author = {}
if not env["COMMIT_AUTHOR"] == "":
	author["name"] = env["COMMIT_AUTHOR"]
if not env["COMMIT_AVATAR"] == "":
	author["icon_url"] = env["COMMIT_AVATAR"]

payload = {
	"embeds": [
		{
			"color": color,
			"author": author,
			"title": '[' + env["REPO_NAME"] + ':' + env["BRANCH"] + "] " + str(len(commits)) + " new " + env["EVENT_TYPE"] + ('' if len(commits) == 1 else 's'),
			"url": "http://github.com/" + env["REPO_SLUG"] + '/' + query,
			"description": env["COMMIT_MESSAGE"],
			"timestamp": timestamp
		}
	]
}

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

r = requests.post(DISCORD_WEBHOOK,data=json.dumps(payload),headers={"Content-type": "application/json"})
