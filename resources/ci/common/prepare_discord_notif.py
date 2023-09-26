import common
import datetime                       # timestamps
import json                           # json manipulation
import os                             # for env vars
import pytz                           # timezones
import requests                       # http requests
from argparse import ArgumentParser   # for argument variables
from json.decoder import JSONDecodeError

def prepare_discord_notif():
  CI_SETTINGS = {}
  manifest_path = os.path.join(".","resources","app","meta","manifests","ci.json")
  if (not os.path.isfile(manifest_path)):
    raise AssertionError("Manifest not found: " + manifest_path)
  with(open(manifest_path)) as ci_settings_file:
    try:
        CI_SETTINGS = json.load(ci_settings_file)
    except JSONDecodeError as e:
        raise ValueError("CI Settings file malformed!")

  # default stuff
  DEFAULT_EVENT = "event"
  DEFAULT_REPO_SLUG = '/'.join(CI_SETTINGS["common"]["common"]["repo"])

  # spiffy colors for embed
  colors = {}
  for name,color in CI_SETTINGS["common"]["prepare_discord_notif"]["colors"].items():
    colors[name] = (int(color,16))

  env = common.prepare_env()  # get env vars

  env["COMMIT_AUTHOR"] = CI_SETTINGS["common"]["prepare_discord_notif"]["travis"]["author"]
  env["COMMIT_AVATAR"] = CI_SETTINGS["common"]["prepare_discord_notif"]["travis"]["avatar"]
  commits = []
  query = ""
  timestamp = ""

  # event log
  event_manifest = {}
  if not env["EVENT_LOG"] == "":
      with(open(env["EVENT_LOG"],"r")) as f:
          try:
              event_manifest = json.load(f)
          except JSONDecodeError as e:
              raise ValueError("Event Log malformed!")

  # branch
  if env["BRANCH"] == "":
      ref = os.getenv("GITHUB_REF", "")
      if not ref == "":
          ref = ref.split('/')
          for varname, check in (
                  ("BRANCH", "heads"),
                  ("TAG", "tag")
          ):
              if ref[1] == check:
                  env[varname] = ref[2]
  if env["BRANCH"] == "":
      env["BRANCH"] = "master"

  # author/avatar
  if "sender" in event_manifest:
      if "avatar_url" in event_manifest["sender"]:
          env["COMMIT_AVATAR"] = event_manifest["sender"]["avatar_url"]
      if "login" in event_manifest["sender"]:
          env["COMMIT_AUTHOR"] = event_manifest["sender"]["login"]
  author = {}
  if not env["COMMIT_AUTHOR"] == "":
      author["name"] = env["COMMIT_AUTHOR"]
  if not env["COMMIT_AVATAR"] == "":
      author["icon_url"] = env["COMMIT_AVATAR"]

  # embed color
  color = 0x000000
  if env["COMMIT_AUTHOR"].lower() in colors:
      color = colors[env["COMMIT_AUTHOR"].lower()]

  # commit ID/message
  if "after" in event_manifest:
      if env["COMMIT_ID"] == "":
          env["COMMIT_ID"] = event_manifest["after"]

  if not env["COMMIT_ID"] == "":
      query = "commit/" + env["COMMIT_ID"]

  if not env["COMMIT_COMPARE"] == "":
      query = "compare/" + env["COMMIT_COMPARE"]

  if env["EVENT_MESSAGE"] == "":
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
                  commit["url"] = commit["url"].replace("***", CI_SETTINGS["common"]["common"]["repo"]["username"])
                  commits.append("[`" + commit["id"][:7] + "`](" +
                                 commit["url"] + ')' + ' ' + commit_title)
  else:
      commit = {}
      commit_message = env["EVENT_MESSAGE"]
      commit["id"] = env["COMMIT_ID"]
      if "\n\n" in commit_message:
          commit_parts = commit_message.split("\n\n")
          commit_title = commit_parts.pop(0)
          commit_message = "\n\n".join(commit_parts)
      else:
          commit_title = commit_message
      commit["url"] = "http://github.com/" + env["REPO_SLUG"] + '/' + query
      commit["url"] = commit["url"].replace("***", CI_SETTINGS["common"]["common"]["repo"]["username"])
      commits.append("[`" + commit["id"][:7] + "`](" +
                     commit["url"] + ')' + ' ' + commit_title)

  # number of commits
  num_events = len(commits)
  if num_events > 0:
      env["EVENT_MESSAGE"] = ""
      if num_events == 1:
          if not env["COMMIT_COMPARE"] == "":
              num_events = "Many"
      for commit in commits:
          env["EVENT_MESSAGE"] += commit + "\n"

  # event type
  if "pull" in env["EVENT_TYPE"]:
      env["PULL_ID"] = os.getenv("TRAVIS_PULL_REQUEST", "")
      env["PULL_BRANCH"] = os.getenv("TRAVIS_PULL_REQUEST_BRANCH", "")
      env["PULL_SHA"] = os.getenv("TRAVIS_PULL_REQUEST_SHA", "")
      query = "pull/" + env["PULL_ID"]

  if "push" in env["EVENT_TYPE"]:
      env["EVENT_TYPE"] = "commit"

  if "release" in env["EVENT_TYPE"]:
      if "action" in event_manifest:
          env["EVENT_TYPE"] = event_manifest["action"] + ' ' + env["EVENT_TYPE"]
      if "release" in event_manifest:
          if "tag_name" in event_manifest["release"]:
              num_events = 1
              env["EVENT_MESSAGE"] = CI_SETTINGS["common"]["common"]["repo"]["title"] + ' ' + \
                  event_manifest["release"]["tag_name"]
              query = "releases/tag/" + event_manifest["release"]["tag_name"]
              if "assets" in event_manifest["release"]:
                  print(event_manifest["release"]["assets"])

  # timestamp
  if timestamp == "":
      if "repository" in event_manifest:
          if "updated_at" in event_manifest["repository"]:
              timestamp = event_manifest["repository"]["updated_at"]

  if timestamp == "":
      utc_now = pytz.utc.localize(datetime.datetime.utcnow())
      pst_now = utc_now.astimezone(pytz.timezone(CI_SETTINGS["common"]["prepare_discord_notif"]["timezone"]))
      timestamp = pst_now.isoformat()
      timestamp = timestamp[:timestamp.find('.')]

  if timestamp != "":
      if '+' in timestamp:
          timestamp = timestamp[:timestamp.find('+')]
      elif '-' in timestamp:
          timestamp = timestamp.split('-')
          _ = timestamp.pop()
          timestamp = '-'.join(timestamp)

  # embed title
  embed_title = ""
  embed_title += '[' + env["REPO_NAME"] + ':' + env["BRANCH"] + "] "
  embed_title += str(num_events) + " new " + env["EVENT_TYPE"]
  if isinstance(num_events, str) or (isinstance(num_events, int) and (not num_events == 1)):
      embed_title += 's'

  # build payload
  payload = {
      "embeds": [
          {
              "color": color,
              "author": author,
              "title": embed_title,
              "url": "http://github.com/" + env["REPO_SLUG"] + '/' + query,
              "description": env["EVENT_MESSAGE"],
              "timestamp": timestamp
          }
      ]
  }

  # get webhook for MegaMan.EXE
  DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

  # send request
  r = requests.post(DISCORD_WEBHOOK, data=json.dumps(payload),
                    headers={"Content-type": "application/json"})


def main():
  prepare_discord_notif()

if __name__ == "__main__":
  main()
else:
  raise AssertionError("Script improperly used as import!")
