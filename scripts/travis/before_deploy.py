import os # for env vars
import subprocess # for shell level stuff

DEPLOY_BINARY = os.getenv("DEPLOY_BINARY","")
DEPLOY_PAGES = os.getenv("DEPLOY_PAGES","")
TRAVIS_REPO_SLUG = os.getenv("TRAVIS_REPO_SLUG","")
TRAVIS_TAG = os.getenv("TRAVIS_TAG","")
RELEASE_NAME = os.getenv("RELEASE_NAME","")

GITHUB_TAG = TRAVIS_TAG

FILES = "../deploy/*"
PAGES = "../pages"
BODY_PATH = "./RELEASENOTES.md"
BODY = "Please see [RELEASENOTES.md]("
BODY += "https://github.com/"
BODY += TRAVIS_REPO_SLUG
BODY += "/blob/"
BODY += GITHUB_TAG
BODY += "/RELEASENOTES.md"
BODY += ") for description."

subprocess.check_call("git tag " + GITHUB_TAG)
#subprocess.check_call("git push origin " + GITHUB_TAG)

print("Deploy Binary:   " + DEPLOY_BINARY)
print("Deploy Pages:    " + DEPLOY_PAGES)
print("Files to Upload: " + FILES)
print("GHPages Staging: " + PAGES)
print("Release Name:    " + RELEASE_NAME)
print("Git tag:         " + GITHUB_TAG)
