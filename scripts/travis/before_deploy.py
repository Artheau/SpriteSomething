import os # for env vars
import subprocess # for shell level stuff

DEPLOY_BINARY = os.environ.get("DEPLOY_BINARY") or "DEPLOY_BINARY"
DEPLOY_PAGES = os.environ.get("DEPLOY_PAGES") or "DEPLOY_PAGES"
TRAVIS_REPO_SLUG = os.environ.get("TRAVIS_REPO_SLUG") or "TRAVIS_REPO_SLUG"
TRAVIS_TAG = os.environ.get("TRAVIS_TAG") or "TRAVIS_TAG"
RELEASE_NAME = os.environ.get("RELEASE_NAME") or "RELEASE_NAME"
FILES = "../deploy/*"
PAGES = "../pages"
BODY_PATH = "./RELEASENOTES.md"
BODY = "Please see [RELEASENOTES.md]("
BODY += "https://github.com/"
BODY += TRAVIS_REPO_SLUG
BODY += "/blob/"
BODY += TRAVIS_TAG
BODY += "/RELEASENOTES.md"
BODY += ") for description."

subprocess.check_call("git tag " + TRAVIS_TAG)
#subprocess.check_call("git push origin " + TRAVIS_TAG)

print("Deploy Binary:   " + DEPLOY_BINARY)
print("Deploy Pages:    " + DEPLOY_PAGES)
print("Files to Upload: " + FILES)
print("GHPages Staging: " + PAGES)
print("Release Name:    " + RELEASE_NAME)
print("Git tag:         " + TRAVIS_TAG)
